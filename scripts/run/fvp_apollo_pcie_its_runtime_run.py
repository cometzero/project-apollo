from __future__ import annotations

from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Final

from fvp_apollo_pcie_its_output import OutputDirectory
from fvp_apollo_pcie_its_profile import (
    RunError,
    VerifiedProfile,
    atomic_write,
    configuration_applied,
    failure_result,
    load_json,
    process_snapshot,
    require_object,
    require_string,
    sha256_file,
)
from fvp_apollo_pcie_its_runtime import (
    FDT_BEGIN,
    FDT_END,
    RUNNER,
    VALIDATOR,
    cleanup_receipt,
    extract_base64_between,
    guest_transport,
    normalize_live_fdt,
    pcie_stall_state,
    primary_uart_path,
    require_endpoint_observables,
    require_runtime_pass,
    require_smmu_clean,
    selected_dt_source,
    stop_process_group,
)
from fvp_apollo_pcie_its_types import (
    FvpResult,
    JsonObject,
    ProcessObservation,
    cleanup_json,
    contract_json,
    json_strings,
    observations_json,
)


WORKSPACE: Final = Path(__file__).resolve().parents[2]


def run(verified: VerifiedProfile, out_dir: OutputDirectory, timeout: int) -> FvpResult:
    runtime_output = out_dir.create_child(f"runtime-{int(time.time())}")
    runtime = runtime_output.path
    runtime_output.close()
    boot_dir = runtime / "boot"
    command = [
        sys.executable,
        str(RUNNER),
        "--machine",
        "apollo-fvp",
        "--fvpconf",
        str(verified.fvpconf),
        "--out-dir",
        str(boot_dir),
        "--timeout",
        str(timeout),
        "--require",
        "all",
        "--post-login-timeout",
        str(min(timeout, 240)),
    ]
    for guest_command in guest_transport(verified.profile_sha256):
        command.extend(["--post-login-command", guest_command])
    started = time.time()
    observations: list[ProcessObservation] = []
    stop_reason = ""
    proc: subprocess.Popen[str] = subprocess.Popen(
        command,
        cwd=WORKSPACE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    deadline, seen, primary_size, last_progress = (
        time.monotonic() + timeout + 90,
        set[tuple[int, tuple[str, ...]]](),
        0,
        time.monotonic(),
    )
    while proc.poll() is None and time.monotonic() < deadline:
        for observation in process_snapshot(proc.pid):
            key = (observation["pid"], tuple(observation["argv"]))
            if key not in seen:
                seen.add(key)
                observations.append(observation)
        primary_size, last_progress, stalled = pcie_stall_state(
            boot_dir, primary_size, last_progress
        )
        if stalled:
            stop_reason = "pcie_config_read_stall"
            stop_process_group(proc, signal.SIGINT)
            break
        time.sleep(0.2)
    if proc.poll() is None:
        stop_process_group(proc, signal.SIGINT)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            stop_process_group(proc, signal.SIGKILL)
    stdout, _ = proc.communicate(timeout=10)
    (runtime / "wrapper.stdout.log").write_text(
        stdout, encoding="utf-8", errors="replace"
    )
    applied = configuration_applied(verified, observations, stdout)
    detail: JsonObject = {
        "runner_command": json_strings(command),
        "runner_pid": proc.pid,
        "started_unix": started,
        "ended_unix": time.time(),
        "runner_rc": proc.returncode,
        "observed_fvp_processes": observations_json(observations),
        "configuration_applied": applied,
        "stop_reason": stop_reason,
        "last_primary_progress_monotonic": last_progress,
    }
    if not applied:
        return failure_result(
            "fvp_process_unobserved", verified.profile_sha256, out_dir, detail
        )
    if stop_reason:
        return failure_result(
            stop_reason, verified.profile_sha256, out_dir, detail, True
        )
    boot_result_path = boot_dir / "result.json"
    if proc.returncode != 0 or not boot_result_path.is_file():
        return failure_result(
            "canonical_runner_failed",
            verified.profile_sha256,
            out_dir,
            detail,
            True,
        )
    boot_result = load_json(boot_result_path)
    post_login = require_object(
        boot_result.get("post_login"), "child_pass_semantic_fail"
    )
    if boot_result.get("passed") is not True or post_login.get("done") is not True:
        return failure_result(
            "child_pass_semantic_fail",
            verified.profile_sha256,
            out_dir,
            detail,
            True,
        )
    status = require_object(boot_result.get("status"), "scp_rnsam_missing")
    consoles = require_object(status.get("consoles"), "scp_rnsam_missing")
    scp = require_object(
        consoles.get("terminal_uart_si_cluster0"), "scp_rnsam_missing"
    )
    scp_path = Path(require_string(scp, "path", "scp_rnsam_missing"))
    if not scp_path.is_file() or "RNSAM setup complete" not in scp_path.read_text(
        encoding="utf-8", errors="replace"
    ):
        return failure_result(
            "scp_rnsam_missing", verified.profile_sha256, out_dir, detail, True
        )
    primary = primary_uart_path(boot_result)
    primary_text = primary.read_text(encoding="utf-8", errors="replace")
    guest_log = runtime / "apollo-pcie-its-guest.log"
    guest_log.write_text(
        "\n".join(
            line for line in primary_text.splitlines() if line.startswith("APOLLO_IRQ|")
        )
        + "\n",
        encoding="utf-8",
    )
    normalized = runtime / "normalized-its.json"
    validation = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--log",
            str(guest_log),
            "--platform",
            "fvp",
            "--mode",
            "msix",
            "--input-sha256",
            verified.profile_sha256,
            "--output",
            str(normalized),
        ],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        check=False,
    )
    (runtime / "validator.stdout.log").write_text(
        validation.stdout + validation.stderr, encoding="utf-8"
    )
    try:
        runtime_evidence = require_runtime_pass(normalized)
        require_endpoint_observables(primary_text)
        require_smmu_clean(primary_text)
        live_dtb = runtime / "live-fdt.dtb"
        live_dtb.write_bytes(extract_base64_between(primary_text, FDT_BEGIN, FDT_END))
        live_hash = sha256_file(live_dtb)
        live_contract = normalize_live_fdt(live_dtb, verified.dt_contract)
        dt_source = selected_dt_source(verified, live_hash)
    except RunError as error:
        return failure_result(
            error.reason,
            verified.profile_sha256,
            out_dir,
            {**detail, "error": error.detail},
            True,
        )
    cleanup = cleanup_receipt(observations)
    if not cleanup["clean"]:
        return failure_result(
            "cleanup_missing",
            verified.profile_sha256,
            out_dir,
            {**detail, "cleanup": cleanup_json(cleanup)},
            True,
        )
    payload: FvpResult = {
        "schema_version": 1,
        "status": "pass",
        "reason": "ok",
        "profile_sha256": verified.profile_sha256,
        "configuration_applied": True,
        "qbox_started": False,
        "detail": {
            **detail,
            "boot_result": str(boot_result_path),
            "primary_uart": str(primary),
            "normalized_its": runtime_evidence,
            "live_fdt_sha256": live_hash,
            "live_dt_contract": contract_json(live_contract),
            "dt_source": dt_source,
            "cleanup": cleanup_json(cleanup),
        },
    }
    atomic_write(out_dir, payload)
    return payload
