from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_qbox_yocto_boot_regression.py"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def result_tree(root: Path, *, login_elapsed: float = 10.0, error_line: str | None = None) -> Path:
    root.mkdir(parents=True)
    progress_hits = {
        "rse_bl1_1": {"elapsed_s": 1.0, "marker": "Starting TF-M BL1_1"},
        "rse_jump_bl1_2": {"elapsed_s": 2.0, "marker": "Jumping to BL1_2"},
        "rse_bl1_2": {"elapsed_s": 3.0, "marker": "Starting TF-M BL1_2"},
        "rse_attempt_image_0": {"elapsed_s": 4.0, "marker": "Attempting to boot image 0"},
        "rse_bl2_decrypted": {"elapsed_s": 5.0, "marker": "BL2 image decrypted successfully"},
        "rse_bl2_validated": {"elapsed_s": 6.0, "marker": "BL2 image validated successfully"},
        "rse_jump_bl2": {"elapsed_s": 6.1, "marker": "Jumping to BL2"},
        "rse_image_4_loaded": {"elapsed_s": 6.5, "marker": "Image 4 loaded from the primary slot"},
        "rse_image_3_loaded": {"elapsed_s": 7.0, "marker": "Image 3 loaded from the primary slot"},
        "rse_image_2_loaded": {"elapsed_s": 7.5, "marker": "Image 2 loaded from the primary slot"},
        "rse_image_0_loaded": {"elapsed_s": 8.0, "marker": "Image 0 loaded from the primary slot"},
        "rse_scp_power_on_ap": {
            "elapsed_s": 8.5,
            "marker": "RSE to SCP SCMI power on AP succeeded",
        },
        "rse_first_image_slot": {"elapsed_s": 8.7, "marker": "Jumping to the first image slot"},
        "measured_boot_bl33": {"elapsed_s": 9.0, "marker": "BL_33"},
        "primary_linux_cpu": {"elapsed_s": 9.5, "marker": "Booting Linux on physical CPU"},
        "primary_login_prompt": {"elapsed_s": login_elapsed, "marker": "apollo-fvp login:"},
    }
    profile_markers = [
        {
            "name": name,
            "label": name,
            "marker": hit["marker"],
            "seen": True,
            "elapsed_s": hit["elapsed_s"],
        }
        for name, hit in progress_hits.items()
    ]
    rd_result = {
        "passed": True,
        "blocker": None,
        "console_logs": {
            "primary_console": str(root / "qbox-primary-console.log"),
            "rse": str(root / "qbox-rse.log"),
            "scp": str(root / "qbox-safety-island-cl0.log"),
            "secure_console": str(root / "qbox-secure-console.log"),
        },
        "fail_patterns": {
            "Kernel panic": False,
            "Unable to mount root fs": False,
            "No working init found": False,
            "[ERR]": False,
            "[ERROR]": False,
        },
        "progress_marker_first_hits": progress_hits,
        "rse_boot_timing_profile": {"markers": profile_markers, "deltas": [], "summary": {}},
    }
    result = {
        "passed": True,
        "blocker": None,
        "child_result": str(root / "rd-aspen-result.json"),
        "console_logs": {
            "platform": str(root / "qbox-platform.log"),
            "primary_console": str(root / "qbox-primary-console.log"),
            "rse": str(root / "qbox-rse.log"),
            "secure_console": str(root / "qbox-secure-console.log"),
            "si_cl0": str(root / "qbox-safety-island-cl0.log"),
            "si_cl1": str(root / "qbox-safety-island-cl1.log"),
        },
        "rse_boot_timing_profile": rd_result["rse_boot_timing_profile"],
    }
    write(root / "result.json", json.dumps(result))
    write(root / "rd-aspen-result.json", json.dumps(rd_result))
    write(root / "qbox-platform.log", "SystemC boot\n")
    rse_lines = [
        "Starting TF-M BL1_1",
        "Jumping to BL1_2",
        "Starting TF-M BL1_2",
        "Attempting to boot image 0",
        "BL2 image decrypted successfully",
        "BL2 image validated successfully",
        "Jumping to BL2",
        "Image 4 loaded from the primary slot",
        "Image 3 loaded from the primary slot",
        "Image 2 loaded from the primary slot",
        "Image 0 loaded from the primary slot",
        "RSE to SCP SCMI power on AP succeeded",
        "Jumping to the first image slot",
        "BL_33",
    ]
    if error_line:
        rse_lines.append(error_line)
    write(root / "qbox-rse.log", "\n".join(rse_lines) + "\n")
    write(
        root / "qbox-safety-island-cl0.log",
        "\n".join(
            [
                "[    0.001000] [GICX00-MULTIVIEW] SI GIC-multiview configured successfully",
                "[    0.002000] [SI0_PLATFORM] SCP started",
                "[    0.003000] [FWK] Module initialization complete!",
            ]
        )
        + "\n",
    )
    write(
        root / "qbox-safety-island-cl1.log",
        "\n".join(
            [
                "Out of Reset (OoR) completed on CPU: 0",
                "*** Booting Zephyr OS build v4.1.0 ***",
                "[00:00:00.120,000] <inf> pfdi_agent: PFDI Agent setup complete",
                "[00:00:00.240,000] <inf> pfdi_mgmt: PFDI service ready (4 CPUs)",
                "[00:00:00.250,000] <inf> si_net_init: Network interface configured",
            ]
        )
        + "\n",
    )
    write(
        root / "qbox-secure-console.log",
        "\n".join(
            [
                "NOTICE:  BL2: v2.14.0",
                "NOTICE:  BL31: v2.14.0",
                "I/TC: OP-TEE version: test",
            ]
        )
        + "\n",
    )
    write(
        root / "qbox-primary-console.log",
        "\n".join(
            [
                "U-Boot 2026.01 apollo_fvp",
                "Booting Linux on physical CPU 0x0000000000",
                "arch_timer: cp15 timer running at 125.00MHz (phys).",
                "arch-timer-mmio 1a810000.timer: mmio timer running at 125.00MHz (phys)",
                "Linux version test",
                "apollo-fvp login: root",
                "root@apollo-fvp:~# echo __QBOX_PROBE_DONE__",
                "__QBOX_PROBE_DONE__",
            ]
        )
        + "\n",
    )
    return root


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def wait_for_file(path: Path, timeout_s: float = 5.0) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if path.exists():
            return
        time.sleep(0.05)
    raise AssertionError(f"timed out waiting for {path}")


def wait_for_process_exit(pid: int, timeout_s: float = 5.0) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if not process_exists(pid):
            return
        time.sleep(0.05)
    raise AssertionError(f"process still exists: {pid}")


def test_run_qbox_yocto_boot_regression_records_and_checks_baseline(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    current_result = result_tree(tmp_path / "current")
    baseline = tmp_path / "baseline.json"

    recorded = run_cli(
        "--record-baseline",
        "--baseline",
        str(baseline),
        "--result-dir",
        str(baseline_result),
    )
    assert recorded.returncode == 0, recorded.stderr
    assert baseline.exists()

    checked = run_cli("--baseline", str(baseline), "--result-dir", str(current_result))
    assert checked.returncode == 0, checked.stderr
    assert '"passed": true' in checked.stdout
    assert "PASS boot stage: rse_bl1_1" in checked.stdout
    assert "baseline_elapsed_s=1.000" in checked.stdout
    assert "current_elapsed_s=1.000" in checked.stdout
    assert "threshold=+20.0%" in checked.stdout


def test_record_baseline_uses_live_timing_for_timestampless_logs(tmp_path: Path) -> None:
    result = result_tree(tmp_path / "result")
    baseline = tmp_path / "baseline.json"
    live_elapsed = 6.25
    write(
        result / "qbox-live-line-timing.json",
        json.dumps(
            {
                "line_elapsed_s": {
                    f"{(result / 'qbox-rse.log').resolve()}:2": live_elapsed,
                },
            }
        ),
    )

    checked = run_cli(
        "--record-baseline",
        "--baseline",
        str(baseline),
        "--result-dir",
        str(result),
    )

    assert checked.returncode == 0, checked.stderr
    data = json.loads(baseline.read_text(encoding="utf-8"))
    stage = next(item for item in data["stages"] if item["name"] == "rse_jump_bl1_2")
    assert stage["elapsed_s"] == live_elapsed
    assert stage["source"].endswith("+live_line_timing")


def test_record_baseline_keeps_nul_prefixed_stage_untimed(tmp_path: Path) -> None:
    result = result_tree(tmp_path / "result")
    baseline = tmp_path / "baseline.json"
    rse_log = result / "qbox-rse.log"
    rse_log.write_text(
        rse_log.read_text(encoding="utf-8").replace(
            "Starting TF-M BL1_2", "\0Starting TF-M BL1_2", 1
        ),
        encoding="utf-8",
    )
    write(
        result / "qbox-live-line-timing.json",
        json.dumps(
            {
                "line_elapsed_s": {
                    f"{rse_log.resolve()}:3": 99.0,
                },
            }
        ),
    )

    checked = run_cli(
        "--record-baseline",
        "--baseline",
        str(baseline),
        "--result-dir",
        str(result),
    )

    assert checked.returncode == 0, checked.stderr
    data = json.loads(baseline.read_text(encoding="utf-8"))
    stage = next(item for item in data["stages"] if item["name"] == "rse_bl1_2")
    assert stage["seen"] is True
    assert stage["elapsed_s"] is None


def test_record_baseline_allows_missing_optional_si_cl1_markers(tmp_path: Path) -> None:
    result = result_tree(tmp_path / "result")
    baseline = tmp_path / "baseline.json"
    write(
        result / "qbox-safety-island-cl1.log",
        "\n".join(
            [
                "Out of Reset (OoR) completed on CPU: 0",
                "*** Booting Zephyr OS build v4.1.0 ***",
            ]
        )
        + "\n",
    )

    checked = run_cli(
        "--record-baseline",
        "--baseline",
        str(baseline),
        "--result-dir",
        str(result),
    )

    assert checked.returncode == 0, checked.stderr
    data = json.loads(baseline.read_text(encoding="utf-8"))
    for name in (
        "si_cl1_pfdi_agent",
        "si_cl1_pfdi_service",
        "si_cl1_network_configured",
    ):
        stage = next(item for item in data["stages"] if item["name"] == name)
        assert stage["optional"] is True
        assert stage["seen"] is False


def test_current_run_may_omit_optional_si_cl1_markers(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    current_result = result_tree(tmp_path / "current")
    baseline = tmp_path / "baseline.json"
    write(
        current_result / "qbox-safety-island-cl1.log",
        "\n".join(
            [
                "Out of Reset (OoR) completed on CPU: 0",
                "*** Booting Zephyr OS build v4.1.0 ***",
            ]
        )
        + "\n",
    )

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli("--baseline", str(baseline), "--result-dir", str(current_result))

    assert checked.returncode == 0, checked.stderr
    assert '"passed": true' in checked.stdout


def test_current_run_may_have_slow_optional_si_cl1_markers(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    current_result = result_tree(tmp_path / "current")
    baseline = tmp_path / "baseline.json"
    write(
        current_result / "qbox-safety-island-cl1.log",
        "\n".join(
            [
                "Out of Reset (OoR) completed on CPU: 0",
                "*** Booting Zephyr OS build v4.1.0 ***",
                "[00:00:00.140,000] <inf> pfdi_agent: PFDI Agent setup complete",
                "[00:00:00.300,000] <inf> pfdi_mgmt: PFDI service ready (4 CPUs)",
                "[00:00:00.320,000] <inf> si_net_init: Network interface configured",
            ]
        )
        + "\n",
    )

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli("--baseline", str(baseline), "--result-dir", str(current_result))

    assert checked.returncode == 0, checked.stderr
    assert '"passed": true' in checked.stdout


def test_run_qbox_yocto_boot_regression_fails_fast_on_timing(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline", login_elapsed=10.0)
    current_result = result_tree(tmp_path / "current", login_elapsed=12.1)
    baseline = tmp_path / "baseline.json"

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli("--baseline", str(baseline), "--result-dir", str(current_result))
    assert checked.returncode == 1
    assert "boot timing regression detected" in checked.stderr
    assert "primary_login_prompt" in checked.stderr
    assert "current_elapsed_s: 12.100" in checked.stderr


def test_run_qbox_yocto_boot_regression_fails_fast_on_error_log(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    current_result = result_tree(tmp_path / "current", error_line="[ERROR] CC3XX backend failed")
    baseline = tmp_path / "baseline.json"

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli("--baseline", str(baseline), "--result-dir", str(current_result))
    assert checked.returncode == 1
    assert "error log regression detected" in checked.stderr
    assert "[ERROR] CC3XX backend failed" in checked.stderr


def test_run_qbox_yocto_boot_regression_waits_for_async_runner(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    template_result = result_tree(tmp_path / "template")
    baseline = tmp_path / "baseline.json"
    out_dir = tmp_path / "current"
    runner = tmp_path / "fake-runner.sh"
    args_log = tmp_path / "fake-runner.args"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "out=''\n"
        "dry_run=0\n"
        f"printf '%s\\n' \"$*\" > {args_log!s}\n"
        "while (($#)); do\n"
        "  case \"$1\" in\n"
        "    --out-dir) out=\"$2\"; shift 2 ;;\n"
        "    --dry-run) dry_run=1; shift ;;\n"
        "    --) shift; break ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "if [[ \"$dry_run\" == 1 ]]; then\n"
        "  printf 'Headless QBox runner command:\\n'\n"
        "  printf '  python3 fake --rootfs %q/rootfs.img\\n' \"$out\"\n"
        "  exit 0\n"
        "fi\n"
        "mkdir -p \"$out\"\n"
        "printf 'running\\n' > \"$out/qbox-run.status\"\n"
        f"(sleep 0.2; cp -a {template_result!s}/. \"$out\"/; "
        "printf '0\\n' > \"$out/qbox-run.status\"; "
        "touch \"$out/.qbox-run.done\") &\n"
        "printf 'started tmux session: fake\\n'\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli(
        "--run",
        "--runner",
        str(runner),
        "--baseline",
        str(baseline),
        "--out-dir",
        str(out_dir),
        "--timeout",
        "1",
        "--result-wait-timeout",
        "5",
        "--poll-interval",
        "0.05",
        "--",
        "--exit-after-pass",
    )
    assert checked.returncode == 0, checked.stderr
    assert '"passed": true' in checked.stdout
    runner_args = args_log.read_text(encoding="utf-8")
    assert "--headless" in runner_args
    assert "--no-attach" not in runner_args


def test_run_qbox_yocto_boot_regression_fails_during_live_log_scan(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    baseline = tmp_path / "baseline.json"
    out_dir = tmp_path / "current"
    runner = tmp_path / "fake-runner-live-error.sh"
    pidfile = tmp_path / "live-runner.pid"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "out=''\n"
        "dry_run=0\n"
        "while (($#)); do\n"
        "  case \"$1\" in\n"
        "    --out-dir) out=\"$2\"; shift 2 ;;\n"
        "    --dry-run) dry_run=1; shift ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "if [[ \"$dry_run\" == 1 ]]; then\n"
        "  printf 'Headless QBox runner command:\\n'\n"
        "  printf '  python3 fake --rootfs %q/rootfs.img\\n' \"$out\"\n"
        "  exit 0\n"
        "fi\n"
        f"printf '%s\\n' \"$$\" > {pidfile!s}\n"
        "mkdir -p \"$out\"\n"
        "printf 'runner arg has apollo-fvp login:\\n'\n"
        "printf 'Starting TF-M BL1_1\\n' > \"$out/qbox-rse.log\"\n"
        "printf 'booting\\n' > \"$out/qbox-platform.log\"\n"
        "sleep 0.2\n"
        "printf 'Error while setting bool property realized\\n' >> \"$out/qbox-platform.log\"\n"
        "sleep 10\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli(
        "--run",
        "--runner",
        str(runner),
        "--baseline",
        str(baseline),
        "--out-dir",
        str(out_dir),
        "--timeout",
        "30",
        "--poll-interval",
        "0.05",
    )
    assert checked.returncode == 1
    assert "PASS boot stage: rse_bl1_1" in checked.stdout
    assert "PASS boot stage: primary_login_prompt" not in checked.stdout
    assert "error log regression detected" in checked.stderr
    assert "Error while setting bool property realized" in checked.stderr
    assert not process_exists(int(pidfile.read_text(encoding="utf-8")))


def test_live_log_scan_ignores_incomplete_known_error_line(tmp_path: Path) -> None:
    known_error = "[ERROR] known backend failed"
    baseline_result = result_tree(tmp_path / "baseline", error_line=known_error)
    template_result = result_tree(tmp_path / "template", error_line=known_error)
    baseline = tmp_path / "baseline.json"
    out_dir = tmp_path / "current"
    runner = tmp_path / "fake-runner-known-partial-error.sh"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "out=''\n"
        "dry_run=0\n"
        "while (($#)); do\n"
        "  case \"$1\" in\n"
        "    --out-dir) out=\"$2\"; shift 2 ;;\n"
        "    --dry-run) dry_run=1; shift ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "if [[ \"$dry_run\" == 1 ]]; then\n"
        "  printf 'Headless QBox runner command:\\n'\n"
        "  printf '  python3 fake --rootfs %q/rootfs.img\\n' \"$out\"\n"
        "  exit 0\n"
        "fi\n"
        "mkdir -p \"$out\"\n"
        "printf 'Starting TF-M BL1_1\\n' > \"$out/qbox-rse.log\"\n"
        "sleep 0.2\n"
        "printf '[ERROR] known' >> \"$out/qbox-rse.log\"\n"
        "sleep 0.2\n"
        "printf ' backend failed\\n' >> \"$out/qbox-rse.log\"\n"
        f"cp -a {template_result!s}/. \"$out\"/\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli(
        "--run",
        "--runner",
        str(runner),
        "--baseline",
        str(baseline),
        "--out-dir",
        str(out_dir),
        "--timeout",
        "5",
        "--result-wait-timeout",
        "5",
        "--poll-interval",
        "0.05",
    )

    assert checked.returncode == 0, checked.stderr
    assert '"passed": true' in checked.stdout


def test_live_stage_timing_uses_incomplete_marker_start(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    template_result = result_tree(tmp_path / "template")
    baseline = tmp_path / "baseline.json"
    out_dir = tmp_path / "current"
    runner = tmp_path / "fake-runner-partial-stage.sh"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "out=''\n"
        "dry_run=0\n"
        "while (($#)); do\n"
        "  case \"$1\" in\n"
        "    --out-dir) out=\"$2\"; shift 2 ;;\n"
        "    --dry-run) dry_run=1; shift ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "if [[ \"$dry_run\" == 1 ]]; then\n"
        "  printf 'Headless QBox runner command:\\n'\n"
        "  printf '  python3 fake --rootfs %q/rootfs.img\\n' \"$out\"\n"
        "  exit 0\n"
        "fi\n"
        "mkdir -p \"$out\"\n"
        "printf 'Starting TF-M BL1_1\\n' > \"$out/qbox-rse.log\"\n"
        "printf 'Jumping to BL1_2\\n' >> \"$out/qbox-rse.log\"\n"
        "sleep 0.2\n"
        "printf 'Starting TF-M BL1_2' >> \"$out/qbox-rse.log\"\n"
        "sleep 4\n"
        "printf '\\n' >> \"$out/qbox-rse.log\"\n"
        f"cp -a {template_result!s}/. \"$out\"/\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli(
        "--run",
        "--runner",
        str(runner),
        "--baseline",
        str(baseline),
        "--out-dir",
        str(out_dir),
        "--timeout",
        "8",
        "--result-wait-timeout",
        "5",
        "--poll-interval",
        "0.05",
    )

    assert checked.returncode == 0, checked.stderr
    assert "PASS boot stage: rse_bl1_2" in checked.stdout


def test_live_monitor_fails_when_required_stage_is_overdue(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    baseline = tmp_path / "baseline.json"
    baseline_rse_log = baseline_result / "qbox-rse.log"
    write(
        baseline_result / "qbox-live-line-timing.json",
        json.dumps(
            {
                "line_elapsed_s": {
                    f"{baseline_rse_log.resolve()}:1": 1.0,
                    f"{baseline_rse_log.resolve()}:2": 2.0,
                },
            }
        ),
    )
    out_dir = tmp_path / "current"
    runner = tmp_path / "fake-runner-missing-stage.sh"
    pidfile = tmp_path / "missing-stage-runner.pid"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "out=''\n"
        "dry_run=0\n"
        "while (($#)); do\n"
        "  case \"$1\" in\n"
        "    --out-dir) out=\"$2\"; shift 2 ;;\n"
        "    --dry-run) dry_run=1; shift ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "if [[ \"$dry_run\" == 1 ]]; then\n"
        "  printf 'Headless QBox runner command:\\n'\n"
        "  printf '  python3 fake --rootfs %q/rootfs.img\\n' \"$out\"\n"
        "  exit 0\n"
        "fi\n"
        f"printf '%s\\n' \"$$\" > {pidfile!s}\n"
        "mkdir -p \"$out\"\n"
        "printf 'Starting TF-M BL1_1\\n' > \"$out/qbox-rse.log\"\n"
        "sleep 10\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    started = time.monotonic()
    checked = run_cli(
        "--run",
        "--runner",
        str(runner),
        "--baseline",
        str(baseline),
        "--out-dir",
        str(out_dir),
        "--timeout",
        "30",
        "--poll-interval",
        "0.05",
    )

    assert checked.returncode == 1
    assert time.monotonic() - started < 8
    assert "boot stage overdue in current run" in checked.stderr
    assert "rse_jump_bl1_2" in checked.stderr
    wait_for_process_exit(int(pidfile.read_text(encoding="utf-8")))


def test_run_qbox_yocto_boot_regression_kills_escaped_qbox_after_timing_failure(
    tmp_path: Path,
) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    baseline = tmp_path / "baseline.json"
    out_dir = tmp_path / "current"
    image = tmp_path / "shared.wic"
    image.write_text("disk\n", encoding="utf-8")
    holder_ready = tmp_path / "holder.ready"
    holder_pid = tmp_path / "holder.pid"
    holder_script = tmp_path / "platforms-vp"
    holder_script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "exec 9<>\"$1\"\n"
        "printf '%s\\n' \"$$\" > \"$3\"\n"
        "printf ready > \"$2\"\n"
        "while true; do sleep 1; done\n",
        encoding="utf-8",
    )
    holder_script.chmod(0o755)
    runner = tmp_path / "fake-runner-escaped-qbox.sh"
    runner.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "out=''\n"
        "dry_run=0\n"
        "while (($#)); do\n"
        "  case \"$1\" in\n"
        "    --out-dir) out=\"$2\"; shift 2 ;;\n"
        "    --dry-run) dry_run=1; shift ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "if [[ \"$dry_run\" == 1 ]]; then\n"
        "  printf 'Headless QBox runner command:\\n'\n"
        f"  printf '  python3 fake --rootfs {image!s}\\n'\n"
        "  exit 0\n"
        "fi\n"
        "mkdir -p \"$out\"\n"
        f"setsid {holder_script!s} {image!s} {holder_ready!s} {holder_pid!s} &\n"
        f"while [[ ! -f {holder_ready!s} ]]; do sleep 0.01; done\n"
        "printf '[    2.000] Starting TF-M BL1_1\\n' > \"$out/qbox-rse.log\"\n"
        "sleep 10\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)

    assert (
        run_cli(
            "--record-baseline",
            "--baseline",
            str(baseline),
            "--result-dir",
            str(baseline_result),
        ).returncode
        == 0
    )

    checked = run_cli(
        "--run",
        "--runner",
        str(runner),
        "--baseline",
        str(baseline),
        "--out-dir",
        str(out_dir),
        "--timeout",
        "30",
        "--poll-interval",
        "0.05",
    )

    assert checked.returncode == 1
    assert "boot timing regression detected" in checked.stderr
    wait_for_process_exit(int(holder_pid.read_text(encoding="utf-8")))


def test_run_qbox_yocto_boot_regression_kills_qbox_holding_images(tmp_path: Path) -> None:
    baseline_result = result_tree(tmp_path / "baseline")
    template_result = result_tree(tmp_path / "template")
    baseline = tmp_path / "baseline.json"
    out_dir = tmp_path / "current"
    image = tmp_path / "shared.wic"
    image.write_text("disk\n", encoding="utf-8")
    ready = tmp_path / "holder.ready"
    holder_script = tmp_path / "platforms-vp"
    holder_script.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "exec 9<>\"$1\"\n"
        "printf ready > \"$2\"\n"
        "while true; do sleep 1; done\n",
        encoding="utf-8",
    )
    holder_script.chmod(0o755)
    holder = subprocess.Popen(
        [str(holder_script), str(image), str(ready)],
        start_new_session=True,
    )
    try:
        wait_for_file(ready)
        assert holder.poll() is None
        runner = tmp_path / "fake-runner-cleanup.sh"
        runner.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "out=''\n"
            "dry_run=0\n"
            "while (($#)); do\n"
            "  case \"$1\" in\n"
            "    --out-dir) out=\"$2\"; shift 2 ;;\n"
            "    --dry-run) dry_run=1; shift ;;\n"
            "    *) shift ;;\n"
            "  esac\n"
            "done\n"
            "if [[ \"$dry_run\" == 1 ]]; then\n"
            "  printf 'Headless QBox runner command:\\n'\n"
            f"  printf '  python3 fake --rootfs {image!s}\\n'\n"
            "  exit 0\n"
            "fi\n"
            "mkdir -p \"$out\"\n"
            f"cp -a {template_result!s}/. \"$out\"/\n",
            encoding="utf-8",
        )
        runner.chmod(0o755)

        assert (
            run_cli(
                "--record-baseline",
                "--baseline",
                str(baseline),
                "--result-dir",
                str(baseline_result),
            ).returncode
            == 0
        )

        checked = run_cli(
            "--run",
            "--runner",
            str(runner),
            "--baseline",
            str(baseline),
            "--out-dir",
            str(out_dir),
            "--timeout",
            "1",
            "--poll-interval",
            "0.05",
        )
        assert checked.returncode == 0, checked.stderr
        assert "pre-run cleanup: QBox pid" in checked.stdout
        assert holder.poll() is not None
    finally:
        if holder.poll() is None:
            holder.terminate()
            holder.wait(timeout=5)
