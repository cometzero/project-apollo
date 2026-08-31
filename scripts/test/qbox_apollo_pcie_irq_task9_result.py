from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

try:
    import qbox_apollo_pcie_irq_task9 as task9
except ModuleNotFoundError:
    from scripts.test import qbox_apollo_pcie_irq_task9 as task9


@dataclass(frozen=True, slots=True)
class ModeResult:
    command: list[str]
    child_pid: int
    child_pgid: int
    rootfs_sha256: str
    primary_log_sha256: str
    result_sha256: str


def write_qualification(
    run_root: Path,
    pins: task9.PinClosure,
    msix: ModeResult,
    intx: ModeResult,
) -> None:
    payload = {
        "schema_version": 1,
        "status": "pass",
        "reason": "ok",
        "run_id": run_root.name.removeprefix("run-"),
        "pins": {
            "fvp_reference_gate_sha256": pins.gate_sha256,
            "source_profile_manifest_sha256": pins.source_profile_sha256,
            "profile_manifest_sha256": pins.profile_sha256,
        },
        "modes": {"msix": asdict(msix), "intx": asdict(intx)},
        "process_cleanup": {"status": "PASS", "residual_pids": []},
        "fvp_qualification": "UNSUPPORTED",
    }
    run_root.joinpath("qualification.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
