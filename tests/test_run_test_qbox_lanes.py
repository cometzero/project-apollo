from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/test"))

from run_test_qbox_lane_defs import (
    QboxInputs,
    QboxLane,
    qbox_yocto_baseline,
    qbox_yocto_result_root,
    runtime_lanes,
)
import run_test_qbox_lanes
from run_test_summary import summarize_run


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "run_test.sh"
EXTRA_LANES = ROOT / "scripts/test/run_test_extra_lanes.py"

type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


def run_runner(*args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [str(RUNNER), *args],
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_extra_lanes(
    run_dir: Path,
    stamp: str,
    *,
    extra_env: dict[str, str] | None = None,
    include_qbox_runtime: bool = False,
    machine: str = "apollo-fvp",
    timeout_fvp: str = "600",
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    absolute_run_dir = ROOT / run_dir if not run_dir.is_absolute() else run_dir
    argv = [
        sys.executable,
        str(EXTRA_LANES),
        "--run-dir",
        str(absolute_run_dir),
        "--stamp",
        stamp,
        "--commands-file",
        str(absolute_run_dir / "commands.jsonl"),
        "--dry-run",
        "--timeout-fvp",
        timeout_fvp,
        "--machine",
        machine,
    ]
    if include_qbox_runtime:
        argv.append("--include-qbox-runtime")
    return subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def load_commands(run_dir: Path) -> list[JsonObject]:
    return [
        json.loads(line)
        for line in (run_dir / "commands.jsonl").read_text(encoding="utf-8").splitlines()
    ]


def argv_text(command: JsonObject) -> str:
    argv = command.get("argv")
    assert isinstance(argv, list)
    return " ".join(str(item) for item in argv)


def command_texts(run_dir: Path) -> list[str]:
    return [argv_text(command) for command in load_commands(run_dir)]


def write_json(path: Path, data: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_default_fvp_context() -> None:
    deploy_dir = ROOT / "build/tmp_baremetal/deploy/images/apollo-fvp"
    fvp_bin = (
        ROOT
        / "build/tmp_baremetal/sysroots-components/x86_64/fvp-rd-aspen-native/usr/bin"
    )
    image_rootfs = (
        ROOT / "build/tmp_baremetal/work/apollo_fvp-poky-linux/nexios-image/1.0/rootfs"
    )
    for path in (deploy_dir, fvp_bin, image_rootfs):
        path.mkdir(parents=True, exist_ok=True)
    (fvp_bin / "FVP_Zena_CSS_Cfg2").write_text("model\n", encoding="utf-8")
    (fvp_bin / "Crypto.so").write_text("plugin\n", encoding="utf-8")
    for name in (
        "nexios-image-apollo-fvp.wic",
        "nexios-image-apollo-fvp.ext4.verity",
        "rse-rom-image.img",
        "rse-flash-image.img",
        "rse-otp-image.img",
        "ap-flash-image.img",
        "combined_provisioning_message.bin",
        "efi-capsule-update-disk-image-fvp-rd-aspen.img",
    ):
        (deploy_dir / name).write_text(name + "\n", encoding="utf-8")
    write_json(
        deploy_dir / "nexios-image-apollo-fvp.testdata.json",
        {
            "DISTRO": "auto-ad-nexios",
            "IMAGE_FSTYPES": "wic ext4.verity",
            "IMAGE_LINK_NAME": "nexios-image-apollo-fvp",
            "IMAGE_ROOTFS": "tmp_baremetal/work/apollo_fvp-poky-linux/nexios-image/1.0/rootfs",
            "MACHINE": "apollo-fvp",
            "PC_CPUS_COUNT_DEFAULT": "4",
            "RD_ASPEN_VARIANT": "cfg2",
            "TEST_FVP_DEVICES": "rtc watchdog networking virtiorng",
            "TEST_SUITES": (
                "ping ssh test_00_rse test_00_secure_partition "
                "test_01_auto_ad_nexios_uki_boot test_02_safety_boot "
                "test_10_linuxboot test_20_aspen_ap_dsu "
                "test_30_configurable_pc_cores fvp_boot fvp_devices"
            ),
            "TEST_TARGET": "HSOCOEFVPTarget",
            "TEST_TARGET_IP": "127.0.0.1:2222",
        },
    )
    write_json(
        deploy_dir / "nexios-image-apollo-fvp.fvpconf",
        {
            "args": ["--plugin", "Crypto.so"],
            "exe": "FVP_Zena_CSS_Cfg2",
            "fvp-bindir": str(fvp_bin),
            "parameters": {
                "css.smb.rseil.rse.rom.raw_image": str(deploy_dir / "rse-rom-image.img"),
                "css.smb.rseil.rse_flashloader.fname": str(
                    deploy_dir / "rse-flash-image.img"
                ),
                "css.smb.rseil.rse.lcm_nvm.raw_image": str(
                    deploy_dir / "rse-otp-image.img"
                ),
                "ros.flash_loader.fname": str(deploy_dir / "ap-flash-image.img"),
                "ros.virtio_block0.image_path": str(
                    deploy_dir / "nexios-image-apollo-fvp.wic"
                ),
                "ros.virtio_block1.image_path": str(
                    deploy_dir / "efi-capsule-update-disk-image-fvp-rd-aspen.img"
                ),
            },
            "data": [
                "css.smb.rseil.rse.sram1="
                + str(deploy_dir / "combined_provisioning_message.bin")
                + "@0x20000"
            ],
        },
    )


def ensure_default_qbox_build_context() -> None:
    (ROOT / "build/local-apollo-fvp/work/qbox-platform").mkdir(parents=True, exist_ok=True)


def reset_run_dir(path: Path) -> None:
    absolute = ROOT / path if not path.is_absolute() else path
    if absolute.exists():
        shutil.rmtree(absolute)


def fake_runtime_script(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "import json",
                "import sys",
                "from pathlib import Path",
                "result = Path(sys.argv[1])",
                "mode = sys.argv[2]",
                "marker = Path(sys.argv[3])",
                "result.parent.mkdir(parents=True, exist_ok=True)",
                "if mode == 'blocked':",
                "    result.write_text(json.dumps({'passed': False, 'blocker': 'blocked_missing_runtime_artifact'}))",
                "    raise SystemExit(1)",
                "if mode == 'fail':",
                "    result.write_text(json.dumps({'passed': False}))",
                "    raise SystemExit(1)",
                "marker.write_text('live ran')",
                "result.write_text(json.dumps({'passed': True, 'blocker': None}))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def fake_lane(tmp_path: Path, name: str, mode: str) -> QboxLane:
    lane_dir = tmp_path / "lanes" / name
    script = tmp_path / "fake_runtime.py"
    marker = tmp_path / f"{name}-ran.txt"
    fake_runtime_script(script)
    result = lane_dir / "result.json"
    return QboxLane(
        name,
        [sys.executable, str(script), str(result), mode, str(marker)],
        [sys.executable, str(script), str(result), mode, str(marker)],
        ROOT,
        lane_dir / "stdout.log",
        lane_dir / "stderr.log",
        lane_dir,
        True,
    )


def command_by_name(commands: list[JsonObject], name: str) -> JsonObject:
    return next(command for command in commands if command.get("name") == name)


def qbox_inputs(
    tmp_path: Path,
    include_runtime: bool = True,
    skip_runtime: bool = False,
    machine: str = "apollo-fvp",
) -> QboxInputs:
    return QboxInputs(
        root=ROOT,
        run_dir=tmp_path / "run",
        commands_file=tmp_path / "run/commands.jsonl",
        dry_run=False,
        include_runtime=include_runtime,
        skip_runtime=skip_runtime,
        timeout_fvp="600",
        machine=machine,
    )


def patch_qbox_lanes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, check_mode: str) -> None:
    build_dir = tmp_path / "qbox-platform"
    build_dir.mkdir()
    monkeypatch.setenv("RUN_TEST_QBOX_BUILD_DIR", str(build_dir))
    monkeypatch.setattr(run_test_qbox_lanes, "static_lanes", lambda inputs: [])
    monkeypatch.setattr(run_test_qbox_lanes, "ctest_lanes", lambda inputs: [])
    monkeypatch.setattr(
        run_test_qbox_lanes,
        "runtime_lanes",
        lambda inputs: [
            fake_lane(tmp_path, "qbox-full-check-only", check_mode),
            fake_lane(tmp_path, "qbox-full-live-cl0-cl1", "pass"),
        ],
    )


def test_qbox_lanes_are_planned() -> None:
    # Given: the default Apollo validation dry-run output directory.
    ensure_default_fvp_context()
    ensure_default_qbox_build_context()
    out_dir = Path("build/tests/task-8-pytest-dry")
    stamp = "task-8-pytest-dry"
    reset_run_dir(out_dir)

    # When: dry-run mode plans extra QBox lanes.
    result = run_runner("--dry-run", "--stamp", stamp, "--out-dir", str(out_dir))
    extra_result = run_extra_lanes(out_dir, stamp)

    # Then: QBox static, CTest, and runtime command records are present.
    assert result.returncode == 0, result.stderr
    assert extra_result.returncode == 0, extra_result.stderr
    commands = command_texts(ROOT / out_dir)
    assert any("validate_qbox_apollo_fvp_full_map.py --out" in command for command in commands)
    assert any("audit_qbox_core_boundary.py --json >" in command for command in commands)
    assert any("audit_qbox_apollo_ap_memory_map.py --check coverage --output" in command for command in commands)
    assert any("validate_qbox_apollo_fvp_boot_sequence.py --static-only --output" in command for command in commands)
    assert any("ctest --test-dir build/local-apollo-fvp/work/qbox-platform -N" in command for command in commands)
    assert any("ctest --test-dir build/local-apollo-fvp/work/qbox-platform -R" in command for command in commands)
    assert any("run_qbox_apollo_fvp_full.py --check-only --si-mode live-cl0-cl1" in command for command in commands)
    assert any("run_qbox_apollo_fvp_full.py --skip-build --si-mode live-cl0-cl1" in command for command in commands)


def test_timeout_fvp_updates_planned_qbox_live_command() -> None:
    # Given: a dry-run with a non-default FVP timeout.
    ensure_default_fvp_context()
    ensure_default_qbox_build_context()
    out_dir = Path("build/tests/task-8-pytest-timeout-fvp")
    stamp = "task-8-pytest-timeout-fvp"
    reset_run_dir(out_dir)

    # When: dry-run mode plans extra QBox lanes.
    result = run_runner(
        "--dry-run",
        "--timeout-fvp",
        "321",
        "--stamp",
        stamp,
        "--out-dir",
        str(out_dir),
    )
    extra_result = run_extra_lanes(out_dir, stamp, timeout_fvp="321")

    # Then: the live QBox runtime record carries the selected timeout.
    assert result.returncode == 0, result.stderr
    assert extra_result.returncode == 0, extra_result.stderr
    commands = load_commands(ROOT / out_dir)
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert "--timeout 321" in argv_text(live)


def test_qvp_yocto_regression_lane_uses_qvp_result_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: the optional Yocto boot-regression lane is enabled for Apollo QVP.
    monkeypatch.setenv("RUN_TEST_QBOX_YOCTO_BOOT_REGRESSION", "1")
    inputs = qbox_inputs(tmp_path, machine="apollo-qvp")

    # When: QBox runtime lanes are planned.
    lanes = runtime_lanes(inputs)

    # Then: the Yocto regression lane uses QVP-specific result and baseline roots.
    lane = next(item for item in lanes if item.name == "qbox-yocto-boot-regression")
    argv = " ".join(lane.argv)
    assert qbox_yocto_result_root(inputs) == ROOT / "build/qbox-apollo-qvp"
    assert qbox_yocto_baseline(inputs) == (
        ROOT / "build/qbox-apollo-qvp/run_qbox_yocto_baseline.json"
    )
    assert "--machine apollo-qvp" in argv
    assert "build/qbox-apollo-qvp/run_qbox_yocto_baseline.json" in argv
    assert "build/qbox-apollo-qvp/regression-" in argv


def test_fvp_yocto_regression_lane_keeps_historical_result_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: the optional Yocto boot-regression lane is enabled for the FVP default.
    monkeypatch.setenv("RUN_TEST_QBOX_YOCTO_BOOT_REGRESSION", "1")
    inputs = qbox_inputs(tmp_path)

    # When: QBox runtime lanes are planned.
    lanes = runtime_lanes(inputs)

    # Then: FVP evidence continues to use the historical FVP result root.
    lane = next(item for item in lanes if item.name == "qbox-yocto-boot-regression")
    argv = " ".join(lane.argv)
    assert qbox_yocto_result_root(inputs) == ROOT / "build/qbox-apollo-fvp"
    assert "--machine apollo-fvp" in argv
    assert "build/qbox-apollo-fvp/run_qbox_yocto_baseline.json" in argv
    assert "qbox-apollo-qvp" not in argv


def test_extra_lanes_plumb_qvp_machine_into_yocto_regression(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: public extra-lanes CLI dry-run is asked to plan Apollo QVP lanes.
    monkeypatch.setenv("RUN_TEST_QBOX_YOCTO_BOOT_REGRESSION", "1")
    ensure_default_fvp_context()
    ensure_default_qbox_build_context()
    out_dir = Path("build/tests/task-8-pytest-qvp-extra")
    stamp = "task-8-pytest-qvp-extra"
    reset_run_dir(out_dir)

    # When: the extra-lanes entry point receives --machine apollo-qvp.
    result = run_extra_lanes(out_dir, stamp, machine="apollo-qvp")

    # Then: the optional Yocto regression lane uses QVP result roots.
    assert result.returncode == 0, result.stderr
    commands = command_texts(ROOT / out_dir)
    assert any("--machine apollo-qvp" in command for command in commands)
    assert any("build/qbox-apollo-qvp/run_qbox_yocto_baseline.json" in command for command in commands)
    assert not any("build/qbox-apollo-fvp/run_qbox_yocto_baseline.json" in command for command in commands)


def test_include_qbox_runtime_missing_build_blocks() -> None:
    # Given: an explicit QBox runtime request with the QBox build directory forced missing.
    ensure_default_fvp_context()
    out_dir = Path("build/tests/task-8-pytest-missing-qbox")
    stamp = "task-8-pytest-missing-qbox"
    reset_run_dir(out_dir)
    missing_qbox_build = ROOT / "build/tests/task-8-fixture/missing-qbox-platform"

    # When: dry-run mode evaluates the QBox runtime prerequisite.
    result = run_runner(
        "--dry-run",
        "--stamp",
        stamp,
        "--out-dir",
        str(out_dir),
    )
    extra_result = run_extra_lanes(
        out_dir,
        stamp,
        extra_env={"RUN_TEST_QBOX_BUILD_DIR": str(missing_qbox_build)},
        include_qbox_runtime=True,
    )

    # Then: explicit runtime is BLOCKED with the QBox missing-build reason.
    assert result.returncode == 0, result.stderr
    assert extra_result.returncode == 2
    summary, exit_code = summarize_run(ROOT / out_dir)
    assert exit_code == 2
    assert summary["status"] == "BLOCKED"
    assert any(
        blocker["reason"] == "blocked_missing_qbox_build"
        for blocker in summary["blockers"]
    )


def test_live_runtime_is_blocked_when_check_only_blocks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox build directory exists but check-only reports a runtime prerequisite blocker.
    patch_qbox_lanes(monkeypatch, tmp_path, "blocked")

    # When: QBox runtime lanes execute through the non-dry-run lane runner.
    rc = run_test_qbox_lanes.run_qbox_lanes(qbox_inputs(tmp_path))

    # Then: live runtime is not launched and the run is BLOCKED, not FAIL.
    assert rc == 2
    assert not (tmp_path / "qbox-full-live-cl0-cl1-ran.txt").exists()
    commands = load_commands(tmp_path / "run")
    check = command_by_name(commands, "qbox-full-check-only")
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert check["status"] == "blocked"
    assert check["blockers"] == [{"reason": "blocked_missing_runtime_artifact"}]
    assert "exit_code" not in check
    assert live["status"] == "blocked"
    assert live["reason"] == "blocked_qbox_check_only_preflight"
    summary, exit_code = summarize_run(tmp_path / "run")
    assert summary["status"] == "BLOCKED"
    assert exit_code == 2


def test_live_runtime_is_skipped_when_check_only_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox build directory exists but check-only fails without a blocker.
    patch_qbox_lanes(monkeypatch, tmp_path, "fail")

    # When: QBox runtime lanes execute through the non-dry-run lane runner.
    rc = run_test_qbox_lanes.run_qbox_lanes(qbox_inputs(tmp_path))

    # Then: live runtime is not launched and the run remains a normal FAIL.
    assert rc == 1
    assert not (tmp_path / "qbox-full-live-cl0-cl1-ran.txt").exists()
    commands = load_commands(tmp_path / "run")
    check = command_by_name(commands, "qbox-full-check-only")
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert check["status"] == "fail"
    assert check["exit_code"] == 1
    assert live["status"] == "skipped"
    assert live["reason"] == "skipped_failed_qbox_check_only"
    summary, exit_code = summarize_run(tmp_path / "run")
    assert summary["status"] == "FAIL"
    assert exit_code == 1


def test_live_runtime_runs_by_default_when_build_exists_and_check_only_passes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox build exists and check-only passes without an explicit runtime request.
    patch_qbox_lanes(monkeypatch, tmp_path, "pass")

    # When: QBox lanes execute in the default mode.
    rc = run_test_qbox_lanes.run_qbox_lanes(qbox_inputs(tmp_path, include_runtime=False))

    # Then: the live runtime process is launched by default.
    assert rc == 0
    assert (tmp_path / "qbox-full-live-cl0-cl1-ran.txt").exists()
    commands = load_commands(tmp_path / "run")
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert live["status"] == "pass"
    assert live["exit_code"] == 0


def test_live_runtime_is_skipped_when_runtime_is_skipped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a QBox build exists and runtime lanes are otherwise runnable.
    patch_qbox_lanes(monkeypatch, tmp_path, "pass")

    # When: QBox lanes execute with the public skip-runtime policy.
    rc = run_test_qbox_lanes.run_qbox_lanes(qbox_inputs(tmp_path, skip_runtime=True))

    # Then: neither check-only nor live runtime is launched.
    assert rc == 0
    assert not (tmp_path / "qbox-full-check-only-ran.txt").exists()
    assert not (tmp_path / "qbox-full-live-cl0-cl1-ran.txt").exists()
    commands = load_commands(tmp_path / "run")
    check = command_by_name(commands, "qbox-full-check-only")
    live = command_by_name(commands, "qbox-full-live-cl0-cl1")
    assert check["status"] == "skipped"
    assert check["reason"] == "skipped_runtime_requested"
    assert live["status"] == "skipped"
    assert live["reason"] == "skipped_runtime_requested"
