from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/test"))

from run_test_oeqa_lanes import OeqaInputs, run_lanes


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_oeqa_lanes.py"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_oeqa(*args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def load_commands(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def make_run_dir(run_dir: Path) -> Path:
    write_json(run_dir / "manifest.json", {"status": "ok", "test_suites": ["ping", "ssh"]})
    commands_file = run_dir / "commands.jsonl"
    commands_file.write_text("", encoding="utf-8")
    return commands_file


def make_oeqa_inputs(root: Path, run_dir: Path, commands_file: Path) -> OeqaInputs:
    return OeqaInputs(
        root=root,
        build_dir=Path("other-build"),
        image="nexios-image",
        run_dir=run_dir,
        commands_file=commands_file,
        timeout_oeqa=10800,
        dry_run=True,
    )


def write_fake_timeout(path: Path, body: str) -> None:
    path.write_text(f"#!/usr/bin/env bash\n{body}\n", encoding="utf-8")
    path.chmod(0o755)


def test_dry_run_plans_current_and_extended_bitbake_commands(tmp_path: Path) -> None:
    # Given: a run directory with a manifest from earlier runner preflight.
    run_dir = tmp_path / "task-9-dry"
    commands_file = make_run_dir(run_dir)

    # When: OEQA lanes are planned in dry-run mode.
    result = run_oeqa(
        "--run-dir",
        str(run_dir),
        "--commands-file",
        str(commands_file),
        "--build-dir",
        "build",
        "--image",
        "nexios-image",
        "--timeout-oeqa",
        "42",
        "--dry-run",
    )

    # Then: both exact BitBake commands and generated conf paths are recorded.
    assert result.returncode == 0, result.stderr
    assert (run_dir / "conf/oeqa-current.conf").is_file()
    assert (run_dir / "conf/oeqa-extended.conf").is_file()
    assert 'TEST_OVERALL_TIMEOUT = "42"' in (
        run_dir / "conf/oeqa-current.conf"
    ).read_text(encoding="utf-8")
    assert 'TEST_OVERALL_TIMEOUT = "42"' in (
        run_dir / "conf/oeqa-extended.conf"
    ).read_text(encoding="utf-8")
    command_text = "\n".join(" ".join(record["argv"]) for record in load_commands(commands_file))
    assert "timeout 42 bash -lc source layers/poky/oe-init-build-env build >/dev/null && bitbake -R " in command_text
    assert "oeqa-current.conf nexios-image -c testimage" in command_text
    assert "oeqa-extended.conf nexios-image -c testimage" in command_text


def test_dry_run_records_shell_data_as_single_tokens_when_values_are_unsafe(tmp_path: Path) -> None:
    # Given: dry-run inputs containing spaces and shell metacharacters.
    run_dir = tmp_path / "run dir; touch RUN_PWNED"
    commands_file = make_run_dir(run_dir)
    build_dir = Path("build dir; touch BUILD_PWNED")
    image = "nexios-image; touch IMAGE_PWNED"

    # When: OEQA lanes are planned in dry-run mode.
    result = run_oeqa(
        "--run-dir",
        str(run_dir),
        "--commands-file",
        str(commands_file),
        "--build-dir",
        str(build_dir),
        "--image",
        image,
        "--dry-run",
    )

    # Then: shell-sensitive values remain data tokens in the bash script.
    assert result.returncode == 0, result.stderr
    records = load_commands(commands_file)
    for record in records:
        assert record["argv"][:4] == ["timeout", "10800", "bash", "-lc"]
        tokens = shlex.split(record["argv"][4])
        assert str(build_dir) in tokens
        assert image in tokens
        assert str(run_dir / "conf" / f"{record['name']}.conf") in tokens
        assert "touch" not in tokens


def test_dry_run_rejects_project_root_run_dir(tmp_path: Path) -> None:
    # Given: dry-run inputs whose run directory resolves to the project root.
    commands_file = tmp_path / "commands.jsonl"

    # When: OEQA lanes are planned against the project root.
    result = run_oeqa(
        "--run-dir",
        ".",
        "--commands-file",
        str(commands_file),
        "--build-dir",
        "build",
        "--image",
        "nexios-image",
        "--dry-run",
    )

    # Then: lane setup is blocked before writing top-level generated confs.
    assert result.returncode == 2
    assert "project root" in result.stderr
    assert not (ROOT / "conf/oeqa-current.conf").exists()
    assert not (ROOT / "conf/oeqa-extended.conf").exists()


def test_dry_run_rejects_active_build_conf_with_alternate_build_dir(tmp_path: Path) -> None:
    # Given: OEQA dry-run inputs using a non-active build directory.
    root = tmp_path / "workspace"
    run_dir = root / "build/conf/bad"
    commands_file = root / "commands.jsonl"
    write_json(run_dir / "manifest.json", {"status": "ok", "test_suites": ["ping"]})

    # When: the lower-level OEQA lane builder targets active build/conf.
    result = run_lanes(make_oeqa_inputs(root, run_dir, commands_file))

    # Then: write_conf rejects the path before OEQA command records are created.
    assert result == 2
    assert not (run_dir / "conf").exists()
    assert not commands_file.exists()


def test_timeout_without_oeqa_failure_json_records_blocked_timeout(tmp_path: Path) -> None:
    # Given: a fake timeout binary that exits with GNU timeout code 124.
    run_dir = tmp_path / "timeout-blocked"
    commands_file = make_run_dir(run_dir)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    write_fake_timeout(fake_bin / "timeout", "exit 124")

    # When: OEQA lanes run and no OEQA failure JSON is produced.
    result = run_oeqa(
        "--run-dir",
        str(run_dir),
        "--commands-file",
        str(commands_file),
        "--build-dir",
        "build",
        "--image",
        "nexios-image",
        "--timeout-oeqa",
        "1",
        extra_env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )

    # Then: timeout is classified as blocked, not as a generic failure.
    assert result.returncode == 2
    records = load_commands(commands_file)
    assert records[0]["status"] == "blocked"
    assert records[0]["blockers"][0]["reason"] == "blocked_timeout"
    assert "exit_code" not in records[0]


def test_timeout_with_real_oeqa_failure_json_records_fail(tmp_path: Path) -> None:
    # Given: a fake timeout binary that writes Yocto OEQA testresults.json before timing out.
    run_dir = tmp_path / "timeout-fail"
    commands_file = make_run_dir(run_dir)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    result_path = run_dir / "oeqa/current/results/testresults.json"
    oeqa_result = {
        "nexios-image-apollo-fvp": {
            "configuration": {"IMAGE_BASENAME": "nexios-image", "MACHINE": "apollo-fvp"},
            "result": {
                "oeqa.runtime.case.TestLinuxBoot.test_linux_boot": {"status": "FAILED"},
                "oeqa.runtime.case.TestSsh.test_ssh": {"status": "PASSED"},
            },
        }
    }
    write_fake_timeout(
        fake_bin / "timeout",
        f"mkdir -p {result_path.parent}; "
        f"cat > {result_path} <<'JSON'\n{json.dumps(oeqa_result)}\nJSON\nexit 124",
    )

    # When: the current OEQA lane times out after writing failure details.
    result = run_oeqa(
        "--run-dir",
        str(run_dir),
        "--commands-file",
        str(commands_file),
        "--build-dir",
        "build",
        "--image",
        "nexios-image",
        "--timeout-oeqa",
        "1",
        extra_env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )

    # Then: the failing OEQA result takes precedence over blocked_timeout.
    assert result.returncode == 1
    records = load_commands(commands_file)
    assert records[0]["status"] == "fail"
    assert records[0]["exit_code"] == 124
    assert any(artifact["kind"] == "oeqa_result" for artifact in records[0]["artifacts"])


def test_oeqa_results_directory_artifacts_only_classify_json_as_result(tmp_path: Path) -> None:
    # Given: a fake OEQA run that leaves both JSON results and text logs in results/.
    run_dir = tmp_path / "mixed-result-artifacts"
    commands_file = make_run_dir(run_dir)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    results_dir = run_dir / "oeqa/current/results/nexios-image"
    result_json = results_dir / "testresults.json"
    boot_log = results_dir / "qemu_boot_log.20260628"
    oeqa_result = {
        "nexios-image-apollo-fvp": {
            "result": {
                "oeqa.runtime.case.TestLinuxBoot.test_linux_boot": {"status": "PASSED"},
            },
        },
    }
    write_fake_timeout(
        fake_bin / "timeout",
        f"mkdir -p {results_dir}; "
        f"cat > {result_json} <<'JSON'\n{json.dumps(oeqa_result)}\nJSON\n"
        f"printf 'boot log\\n' > {boot_log}; exit 0",
    )

    # When: OEQA lane artifacts are recorded.
    result = run_oeqa(
        "--run-dir",
        str(run_dir),
        "--commands-file",
        str(commands_file),
        "--build-dir",
        "build",
        "--image",
        "nexios-image",
        extra_env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )

    # Then: only JSON files are marked as OEQA result evidence.
    assert result.returncode == 0, result.stderr
    records = load_commands(commands_file)
    artifacts = records[0]["artifacts"]
    assert {"kind": "oeqa_result", "path": "oeqa/current/results/nexios-image/testresults.json"} in artifacts
    assert {"kind": "oeqa_result_artifact", "path": "oeqa/current/results/nexios-image/qemu_boot_log.20260628"} in artifacts


@pytest.mark.parametrize("return_code", [0, 124])
def test_malformed_oeqa_result_json_records_blocked_when_command_otherwise_passes(
    tmp_path: Path,
    return_code: int,
) -> None:
    # Given: a fake timeout binary that writes malformed OEQA result JSON.
    run_dir = tmp_path / f"malformed-{return_code}"
    commands_file = make_run_dir(run_dir)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    result_path = run_dir / "oeqa/current/results/testresults.json"
    write_fake_timeout(
        fake_bin / "timeout",
        f"mkdir -p {result_path.parent}; printf '{{not-json' > {result_path}; exit {return_code}",
    )

    # When: the current OEQA lane records otherwise successful or timeout output.
    result = run_oeqa(
        "--run-dir",
        str(run_dir),
        "--commands-file",
        str(commands_file),
        "--build-dir",
        "build",
        "--image",
        "nexios-image",
        "--timeout-oeqa",
        "1",
        extra_env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )

    # Then: malformed evidence is classified as blocked, never pass.
    assert result.returncode == 2
    records = load_commands(commands_file)
    assert records[0]["status"] == "blocked"
    assert records[0]["blockers"][0]["reason"] == "blocked_malformed_oeqa_result"


@pytest.mark.parametrize("body", ["{}", '{"tests": []}'])
def test_parseable_malformed_oeqa_result_json_records_blocked(
    tmp_path: Path,
    body: str,
) -> None:
    # Given: a fake timeout binary that writes parseable but structurally invalid OEQA JSON.
    run_dir = tmp_path / "parseable-malformed"
    commands_file = make_run_dir(run_dir)
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    result_path = run_dir / "oeqa/current/results/testresults.json"
    write_fake_timeout(
        fake_bin / "timeout",
        f"mkdir -p {result_path.parent}; cat > {result_path} <<'JSON'\n{body}\nJSON\nexit 0",
    )

    # When: OEQA lanes record otherwise successful command output.
    result = run_oeqa(
        "--run-dir",
        str(run_dir),
        "--commands-file",
        str(commands_file),
        "--build-dir",
        "build",
        "--image",
        "nexios-image",
        "--timeout-oeqa",
        "1",
        extra_env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
    )

    # Then: malformed OEQA structure is classified as blocked, never pass.
    assert result.returncode == 2
    records = load_commands(commands_file)
    assert records[0]["status"] == "blocked"
    assert records[0]["blockers"][0]["reason"] == "blocked_malformed_oeqa_result"
