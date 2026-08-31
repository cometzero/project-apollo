from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import Final

from fvp_apollo_pcie_its_output import OutputDirectory
from fvp_apollo_pcie_its_profile import (
    RunError,
    VerifiedProfile,
    load_json,
    require_object,
    require_string,
)
from fvp_apollo_pcie_its_types import (
    CleanupReceipt,
    DtContract,
    FvpResult,
    JsonObject,
    ProcessObservation,
)


WORKSPACE: Final = Path(__file__).resolve().parents[2]
RUNNER: Final = WORKSPACE / "scripts/run/runfvp_log_boot.py"
GUEST: Final = WORKSPACE / "scripts/test/apollo_pcie_its_guest.sh"
VALIDATOR: Final = WORKSPACE / "scripts/test/validate_apollo_pcie_its_runtime.py"
FDT_BEGIN: Final = "__APOLLO_LIVE_FDT_BEGIN__"
FDT_END: Final = "__APOLLO_LIVE_FDT_END__"


def extract_base64_between(text: str, begin: str, end: str) -> bytes:
    start = text.find(begin)
    finish = text.find(end, start + len(begin))
    if start < 0 or finish < 0:
        raise RunError("live_fdt_missing")
    try:
        return base64.b64decode(
            "".join(text[start + len(begin) : finish].split()), validate=True
        )
    except ValueError as error:
        raise RunError("live_fdt_malformed") from error


def verify_live_dt(actual: DtContract, expected: DtContract) -> DtContract:
    if actual != expected:
        raise RunError("unexpected_dt_source", json.dumps(actual, sort_keys=True))
    return {
        "node": expected["node"],
        "ecam_base": expected["ecam_base"],
        "its_base": expected["its_base"],
        "smmu_base": expected["smmu_base"],
    }


def normalize_live_fdt(dtb: Path, expected: DtContract) -> DtContract:
    node = expected["node"]
    compatible = subprocess.run(
        ["fdtget", "-t", "s", str(dtb), node, "compatible"],
        capture_output=True,
        text=True,
        check=False,
    )
    if (
        compatible.returncode != 0
        or compatible.stdout.strip() != "pci-host-ecam-generic"
    ):
        raise RunError("unexpected_dt_source", "pcie node")
    targets = (
        (node, expected["ecam_base"]),
        (
            "/soc/interrupt-controller@20800000/msi-controller@20840000",
            expected["its_base"],
        ),
        ("/soc/iommu@1c0000000", expected["smmu_base"]),
    )
    for candidate, expected_base in targets:
        result = subprocess.run(
            ["fdtget", "-t", "x", str(dtb), candidate, "reg"],
            capture_output=True,
            text=True,
            check=False,
        )
        values = [int(value, 16) for value in result.stdout.split()]
        base = (values[0] << 32) | values[1] if len(values) >= 2 else -1
        if result.returncode != 0 or base != int(expected_base, 0):
            raise RunError("unexpected_dt_source", candidate)
    return verify_live_dt(expected, expected)


def require_runtime_pass(path: Path) -> JsonObject:
    payload = load_json(path)
    if payload.get("status") != "pass" or payload.get("reason") != "ok":
        reason = payload.get("reason")
        raise RunError("runtime_contract_fail", reason if isinstance(reason, str) else "missing")
    return payload


def guest_transport(profile_sha256: str) -> list[str]:
    encoded = base64.b64encode(GUEST.read_bytes()).decode("ascii")
    return [
        f"printf %s '{encoded}' | base64 -d >/tmp/apollo-pcie-its-guest.sh && chmod 700 /tmp/apollo-pcie-its-guest.sh",
        "mkdir -p /sys/kernel/debug; mount -t debugfs debugfs /sys/kernel/debug 2>/dev/null || true",
        f"sh /tmp/apollo-pcie-its-guest.sh fvp msix {profile_sha256}; echo __APOLLO_GUEST_RC__$?",
        f"echo {FDT_BEGIN}; base64 /sys/firmware/fdt; echo {FDT_END}",
        "echo __APOLLO_ENDPOINT_BEGIN__; dev=/sys/bus/pci/devices/0004:00:1f.0; test -d $dev && cat $dev/vendor $dev/class && readlink -f $dev/driver && ls -l $dev/resource* && readlink -f $dev/iommu_group; echo __APOLLO_ENDPOINT_END__",
        "echo __APOLLO_SMMU_BEGIN__; dmesg | grep -Eai 'smmu|iommu|fault|abort' || true; echo __APOLLO_SMMU_END__",
    ]


def primary_uart_path(boot_result: JsonObject) -> Path:
    status = require_object(boot_result.get("status"), "primary_uart_missing")
    consoles = require_object(status.get("consoles"), "primary_uart_missing")
    console = require_object(
        consoles.get("terminal_ns_uart0"), "primary_uart_missing"
    )
    path = Path(require_string(console, "path", "primary_uart_missing"))
    if not path.is_file():
        raise RunError("primary_uart_missing")
    return path


def require_endpoint_observables(text: str) -> None:
    begin, end = (
        text.find("__APOLLO_ENDPOINT_BEGIN__"),
        text.find("__APOLLO_ENDPOINT_END__"),
    )
    if begin < 0 or end < 0:
        raise RunError("endpoint_missing")
    if not all(
        value in text[begin:end]
        for value in ("0x13b5", "0x0106", "/ahci", "iommu_group", "resource")
    ):
        raise RunError("endpoint_identity")


def require_smmu_clean(text: str) -> None:
    begin, end = text.find("__APOLLO_SMMU_BEGIN__"), text.find("__APOLLO_SMMU_END__")
    if begin < 0 or end < 0:
        raise RunError("smmu_observation_missing")
    if "fault" in text[begin:end].lower() or "abort" in text[begin:end].lower():
        raise RunError("smmu_fault")


def selected_dt_source(verified: VerifiedProfile, live_sha256: str) -> str:
    delivery = require_object(verified.profile.get("dt_delivery"), "dt_contract_missing")
    firmware = require_object(
        delivery.get("firmware_fip_hw_config"), "dt_contract_missing"
    )
    extracted = require_object(firmware.get("extracted"), "dt_contract_missing")
    expected = require_string(extracted, "sha256", "dt_contract_missing")
    if live_sha256 != expected:
        raise RunError("unexpected_dt_source", "live FDT differs from FIP HW_CONFIG")
    return "prior-stage-x1"


def cleanup_receipt(observations: list[ProcessObservation]) -> CleanupReceipt:
    observed = [item["pid"] for item in observations]
    remaining = [pid for pid in observed if Path(f"/proc/{pid}").exists()]
    return {
        "observed_fvp_pids": observed,
        "remaining_observed_fvp_pids": remaining,
        "clean": not remaining,
    }


def pcie_stall_state(
    boot_dir: Path, previous_size: int, previous_progress: float
) -> tuple[int, float, bool]:
    logs = sorted(boot_dir.glob("terminal_ns_uart0_*.log"))
    if not logs:
        return previous_size, previous_progress, False
    log = logs[0]
    size = log.stat().st_size
    progress = time.monotonic() if size > previous_size else previous_progress
    text = log.read_text(encoding="utf-8", errors="replace")
    return (
        size,
        progress,
        "PCI host bridge to bus 0004:00" in text
        and "0004:00:1f.0" not in text
        and time.monotonic() - progress >= 120,
    )


def stop_process_group(
    process: subprocess.Popen[str], signal_value: signal.Signals
) -> None:
    os.killpg(process.pid, signal_value)


def run(verified: VerifiedProfile, out_dir: OutputDirectory, timeout: int) -> FvpResult:
    from fvp_apollo_pcie_its_runtime_run import run as runtime_run

    return runtime_run(verified, out_dir, timeout)
