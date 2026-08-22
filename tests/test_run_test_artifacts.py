from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/test"))

from run_test_artifacts import normalize_console_logs, write_profile_result  # noqa: E402
from run_test_preflight import _plugin_check  # noqa: E402


def test_plugin_check_hashes_dereferenced_content(tmp_path: Path) -> None:
    # Given: a plugin symlink with a stable user-facing path.
    plugin = tmp_path / "Crypto.so"
    target = tmp_path / "Crypto-v1.so"
    target.write_bytes(b"plugin-v1")
    plugin.symlink_to(target.name)

    # When: preflight resolves and hashes the plugin target.
    first, _ = _plugin_check("plugin:Crypto.so", plugin, "blocked_missing_crypto_plugin")
    target.write_bytes(b"plugin-v2")
    second, _ = _plugin_check("plugin:Crypto.so", plugin, "blocked_missing_crypto_plugin")

    # Then: a same-path content mutation cannot preserve the receipt.
    assert first.resolved_path == str(target)
    assert first.sha256 != second.sha256


def test_pfdi_profile_result_uses_normalized_console_roles(
    tmp_path: Path,
) -> None:
    # Given: raw OEQA FVP console logs with one CPU's PFDI evidence.
    raw_logs = tmp_path / "oeqa/extended/logs"
    raw_logs.mkdir(parents=True)
    (raw_logs / "default_log.txt").write_text(
        "CPU0: Out of Reset (OoR) test OK\n"
        "CPU0: PFDI Online (OnL) test (0 - 40) OK\n"
        "CPU0: injected force error\n",
        encoding="utf-8",
    )
    (raw_logs / "scp_log.txt").write_text(
        "Started PFDI monitoring for AP cluster 0 core 0\n"
        "[FMU] Critical fault received:\n"
        "[SBISTC] SBISTC_EQ_FAIL_CORE0 detected\n",
        encoding="utf-8",
    )

    # When: run-scoped console roles and the profile result are generated.
    outputs = normalize_console_logs(tmp_path, raw_logs)
    result_path = write_profile_result(
        tmp_path,
        {
            "test_profile": "pfdi",
            "backend": "fvp",
            "machine": "apollo-fvp",
            "pc_cpus_count_default": 1,
        },
    )

    # Then: the normalized PFDI result records every observed contract.
    assert {path.name for path in outputs} == {"primary.log", "si-cl0.log"}
    assert result_path is not None
    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert data["fmu_event_count"] == 1
    assert data["cpus"] == [
        {
            "cpu": 0,
            "force_error": True,
            "monitor_started": True,
            "online": True,
            "oor": True,
            "sbistc": True,
        }
    ]


def test_si_cl1_profile_result_records_cpu_observations(
    tmp_path: Path,
) -> None:
    # Given: a normalized SI CL1 console with status, run, and error results.
    console_dir = tmp_path / "logs/consoles"
    console_dir.mkdir(parents=True)
    (console_dir / "si-cl1.log").write_text(
        "pfdi: cpu0 running\n"
        "pfdi: cpu0 rc=0 scheduled: 4, success: 4, skipped: 0\n"
        "pfdi: cpu0 result SUCCESS\n"
        "pfdi: forced error-id 1 on cpu0\n"
        "pfdi: cpu0 result FAILED\n"
        "pfdi: cpu0 firmware: stub implementation detected "
        "(no vendor library)\n",
        encoding="utf-8",
    )

    # When: the SI CL1 profile result is normalized.
    result_path = write_profile_result(
        tmp_path,
        {
            "test_profile": "pfdi-si-cl1",
            "backend": "fvp",
            "machine": "apollo-fvp",
            "pc_cpus_count_default": 4,
        },
    )

    # Then: the CPU-level execution and error transition remain explicit.
    assert result_path == tmp_path / "results/pfdi-si-cl1.json"
    assert result_path is not None
    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert data["cpus"][0] == {
        "cpu": 0,
        "status_seen": True,
        "run_success_seen": True,
        "success_result_seen": True,
        "force_error_seen": True,
        "failed_result_seen": True,
    }
    assert data["firmware_info_seen"] is True


def test_safety_diagnostics_result_records_unity_summaries(
    tmp_path: Path,
) -> None:
    # Given: an SI CL0 console containing passing SSU and FMU Unity output.
    console_dir = tmp_path / "logs/consoles"
    console_dir.mkdir(parents=True)
    (console_dir / "si-cl0.log").write_text(
        "[INTEGRATION_TEST] Start: ssu\n"
        "test_ssu.c:10:test_state_transition:PASS\n"
        "1 Tests 0 Failures 0 Ignored\nOK\n"
        "[INTEGRATION_TEST] End: ssu\n"
        "[INTEGRATION_TEST] Start: fmu\n"
        "test_fmu.c:20:test_fault_collection:PASS\n"
        "1 Tests 0 Failures 0 Ignored\nOK\n"
        "[INTEGRATION_TEST] End: fmu\n",
        encoding="utf-8",
    )

    # When: the safety-diagnostics profile result is normalized.
    result_path = write_profile_result(
        tmp_path,
        {
            "test_profile": "safety-diagnostics-tests",
            "backend": "fvp",
            "machine": "apollo-fvp",
        },
    )

    # Then: totals and pass status remain explicit for both diagnostics.
    assert result_path == tmp_path / "results/safety-diagnostics-tests.json"
    assert result_path is not None
    data = json.loads(result_path.read_text(encoding="utf-8"))
    assert data["diagnostics"] == {
        "fmu": {
            "ended": True,
            "failures": 0,
            "ignored": 0,
            "passed": 1,
            "result": "PASS",
            "started": True,
            "total": 1,
        },
        "ssu": {
            "ended": True,
            "failures": 0,
            "ignored": 0,
            "passed": 1,
            "result": "PASS",
            "started": True,
            "total": 1,
        },
    }
