from __future__ import annotations

import subprocess
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/test"))

from run_test_conf import ConfRequest, PublicRunRequest, public_run_rejection_message, write_conf
from run_test_helpers import load_json, nonempty_lines, run_runner


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_manifest.py"


def run_manifest(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_write_conf_current_when_run_dir_is_safe(tmp_path: Path) -> None:
    # Given: a safe task run directory outside build/conf.
    run_dir = tmp_path / "task-6"

    # When: the current OEQA override conf is requested.
    result = run_manifest(
        "write-conf",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--run-dir",
        str(run_dir),
        "--kind",
        "current",
    )

    # Then: the conf redirects OEQA outputs without pinning TEST_SUITES.
    assert result.returncode == 0, result.stderr
    conf = run_dir / "conf/oeqa-current.conf"
    text = conf.read_text(encoding="utf-8")
    assert f'TEST_LOG_DIR = "{run_dir.resolve()}/oeqa/current/logs"' in text
    assert f'OEQA_JSON_RESULT_DIR = "{run_dir.resolve()}/oeqa/current/results"' in text
    assert f'OEQA_ARTEFACT_DIR = "{run_dir.resolve()}/oeqa/current/artifacts"' in text
    assert 'TEST_OVERALL_TIMEOUT = "' in text
    assert 'TEST_FVP_DEVICES = "rtc watchdog networking virtiorng"' in text
    assert (
        'TEST_FVP_DEVICES:apollo-fvp:auto-ad-nexios = '
        '"rtc watchdog networking virtiorng"'
    ) in text
    assert "cpu_hotplug" not in text
    assert "TEST_SUITES" not in text


def test_auto_ad_nexios_updates_fvp_device_testdata_for_oeqa() -> None:
    distro_conf = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/distro/"
        / "auto-ad-nexios.conf"
    ).read_text(encoding="utf-8")

    assert (
        'TEST_FVP_DEVICES:apollo-fvp:auto-ad-nexios = '
        '"rtc watchdog networking virtiorng"'
    ) in distro_conf
    assert (
        'TESTIMAGE_UPDATE_VARS:append:apollo-fvp:auto-ad-nexios = '
        '" TEST_FVP_DEVICES"'
    ) in distro_conf


def test_write_conf_extended_when_run_dir_is_safe(tmp_path: Path) -> None:
    # Given: a safe task run directory outside build/conf.
    run_dir = tmp_path / "task-6"

    # When: the extended OEQA override conf is requested.
    result = run_manifest(
        "write-conf",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--run-dir",
        str(run_dir),
        "--kind",
        "extended",
    )

    # Then: it pins the non-Xen extended suite.
    assert result.returncode == 0, result.stderr
    text = (run_dir / "conf/oeqa-extended.conf").read_text(encoding="utf-8")
    tokens = text.replace('"', " ").split()
    assert 'TEST_SUITES = "' in text
    assert 'TEST_FVP_DEVICES = "rtc watchdog networking virtiorng"' in text
    assert "cpu_hotplug" not in text
    assert "test_70_mission_based_profiles" not in text
    assert "test_10_pfdi" not in tokens
    assert "test_10_ras_cpu" not in tokens
    assert "test_10_sbistc_integration" not in tokens
    assert "test_20_hipc_baremetal" not in tokens
    assert "test_50_cryptographic_extension" not in tokens
    assert "test_99_uefi_secure_boot" not in text
    assert "test_100_fwu" not in text
    assert "test_40_virtualization" not in text
    assert "test_41_rt_patch_presence" not in text
    assert "domu" not in text.lower()
    assert "xen" not in text.lower()


def test_write_conf_rejects_build_conf_run_dir() -> None:
    # Given: a protected build/conf path.
    forbidden = ROOT / "build/conf/bad"
    if forbidden.exists():
        raise AssertionError(f"unexpected pre-existing forbidden path: {forbidden}")

    # When: write-conf is pointed at build/conf.
    result = run_manifest(
        "write-conf",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--run-dir",
        "build/conf/bad",
        "--kind",
        "current",
    )

    # Then: it fails before creating any file below build/conf.
    assert result.returncode != 0
    assert not forbidden.exists()
    assert "build/conf" in result.stderr


def test_write_conf_rejects_active_build_conf_with_alternate_build_dir(tmp_path: Path) -> None:
    # Given: a lower-level conf request using a non-active build directory.
    forbidden = tmp_path / "build/conf/bad"
    request = ConfRequest(
        root=tmp_path,
        build_dir=Path("other-build"),
        machine="apollo-fvp",
        run_dir=Path("build/conf/bad"),
        kind="current",
    )

    # When: temporary OEQA conf generation targets active build/conf.
    result = write_conf(request, {"status": "ok"})

    # Then: the active project build/conf tree is still rejected.
    assert result.status == "rejected"
    assert result.conf_path is None
    assert not forbidden.exists()
    assert "build/conf" in result.message


def test_write_conf_rejects_project_root_run_dir() -> None:
    # Given: a run directory that resolves to the project root.
    root_conf = ROOT / "conf/oeqa-current.conf"

    # When: write-conf is pointed at the project root.
    result = run_manifest(
        "write-conf",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--run-dir",
        ".",
        "--kind",
        "current",
    )

    # Then: it fails before creating a top-level generated conf.
    assert result.returncode != 0
    assert not root_conf.exists()
    assert "project root" in result.stderr


def test_public_guard_rejects_out_dirs_outside_build_tests() -> None:
    # Given: public runner output paths outside the selected build/tests directory.
    rejected = (
        Path("build/not-tests/bad"),
        Path("/tmp/aas-outside-build-tests"),
        Path(".omo/evidence/bad"),
    )

    # When: each path is checked by the public run guard.
    messages = [
        public_run_rejection_message(PublicRunRequest(ROOT, Path("build"), run_dir))
        for run_dir in rejected
    ]

    # Then: each path is rejected before the shell runner can create artifacts.
    assert all(message is not None for message in messages)
    assert all("outside" in str(message) for message in messages)


def test_public_guard_accepts_build_tests_child() -> None:
    # Given: a public runner output path below the selected build/tests directory.
    request = PublicRunRequest(ROOT, Path("build"), Path("build/tests/ok"))

    # When: it is checked by the public run guard.
    message = public_run_rejection_message(request)

    # Then: it is accepted.
    assert message is None


def test_public_guard_uses_project_build_tests_when_build_dir_is_alternate() -> None:
    # Given: alternate Yocto build dirs and public output paths below their tests dirs.
    rejected = (
        PublicRunRequest(ROOT, Path("other-build"), Path("other-build/tests/probe-escape")),
        PublicRunRequest(ROOT, Path("/tmp/aas-alt-build"), Path("/tmp/aas-alt-build/tests/probe-escape")),
    )
    accepted = PublicRunRequest(ROOT, Path("other-build"), Path("build/tests/probe-ok"))

    # When: each request is checked by the public run guard.
    rejected_messages = [public_run_rejection_message(request) for request in rejected]
    accepted_message = public_run_rejection_message(accepted)

    # Then: --build-dir cannot redirect public artifacts away from project build/tests.
    assert all(message is not None for message in rejected_messages)
    assert all("build/tests" in str(message) for message in rejected_messages)
    assert accepted_message is None


def test_public_guard_rejects_project_build_tests_parent() -> None:
    # Given: the public output directory is the project build/tests parent itself.
    request = PublicRunRequest(ROOT, Path("other-build"), Path("build/tests"))

    # When: it is checked by the public run guard.
    message = public_run_rejection_message(request)

    # Then: every run must live below a stamped child directory.
    assert message is not None
    assert "outside" in message


def test_public_guard_rejects_active_build_conf_as_selected_build_dir() -> None:
    # Given: the selected build directory is the active protected build/conf tree.
    request = PublicRunRequest(ROOT, Path("build/conf"), Path("build/conf/tests/bad"))

    # When: it is checked by the public run guard.
    message = public_run_rejection_message(request)

    # Then: it is rejected before deriving build/conf/tests artifacts.
    assert message is not None
    assert "protected build directory" in message


def test_public_runner_default_out_dir_ignores_alternate_build_dir() -> None:
    # Given: an alternate Yocto build directory and no explicit output directory.
    stamp = "task-artifact-root-alt-build-default"
    out_dir = ROOT / "build/tests" / stamp
    escaped_out_dir = ROOT / "other-build/tests" / stamp
    shutil.rmtree(out_dir, ignore_errors=True)
    shutil.rmtree(escaped_out_dir, ignore_errors=True)

    # When: dry-run mode derives its default public artifact root.
    result = run_runner("--build-dir", "other-build", "--dry-run", "--stamp", stamp)

    # Then: public artifacts still land under project build/tests/<stamp>.
    assert result.returncode == 0, result.stderr
    assert nonempty_lines(result.stdout)[-2:] == [
        "RESULT: PASS",
        f"SUMMARY: build/tests/{stamp}/summary.json",
    ]
    assert (out_dir / "summary.json").is_file()
    assert not escaped_out_dir.exists()


def test_public_runner_rejects_alternate_build_dir_tests_escape() -> None:
    # Given: an alternate build-dir tests path that used to be accepted.
    out_dir = ROOT / "other-build/tests/probe-escape"
    shutil.rmtree(out_dir, ignore_errors=True)

    # When: dry-run mode is requested with that public output path.
    result = run_runner(
        "--build-dir",
        "other-build",
        "--out-dir",
        "other-build/tests/probe-escape",
        "--dry-run",
    )

    # Then: it fails as a usage error before creating escaped artifacts.
    assert result.returncode == 64
    assert "build/tests" in result.stderr
    assert not out_dir.exists()


def test_public_runner_writes_domu_exclusion_to_artifacts() -> None:
    # Given: an explicit dry-run output directory under project build/tests.
    stamp = "task-domu-exclusion"
    out_dir = Path("build/tests") / stamp
    shutil.rmtree(ROOT / out_dir, ignore_errors=True)

    # When: dry-run mode writes the plan, excluded sidecar, and summary.
    result = run_runner("--dry-run", "--stamp", stamp, "--out-dir", str(out_dir))

    # Then: all public exclusion artifacts carry DomU evidence.
    assert result.returncode == 0, result.stderr
    for name in ("plan.json", "excluded.json", "summary.json"):
        text = (ROOT / out_dir / name).read_text(encoding="utf-8")
        assert "DomU" in text or "domu" in text
    excluded_ids = {item["id"] for item in load_json(ROOT / out_dir / "excluded.json")["excluded"]}
    assert {"test_40_virtualization", "domu-lifecycle"}.issubset(excluded_ids)
