from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
from typing import Final, TypeAlias

from run_test_safety_diagnostics import write_safety_diagnostics_result


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]

CONSOLE_ALIASES: Final = {
    "default": "primary",
    "tf-a": "secure",
    "secure": "secure",
    "rse": "rse",
    "scp": "si-cl0",
    "safety_island_c1": "si-cl1",
}


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _write_json_atomic(path: Path, data: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def append_test_event(
    run_dir: Path,
    event: str,
    name: str,
    status: str,
) -> None:
    record: JsonObject = {
        "event": event,
        "name": name,
        "status": status,
        "timestamp": _now(),
    }
    with (run_dir / "events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    _write_json_atomic(
        run_dir / "status.json",
        {
            "state": "running",
            "last_event": record,
            "updated_at": _now(),
        },
    )


def _console_source(logs_dir: Path, alias: str) -> Path | None:
    candidates = sorted(logs_dir.glob(f"{alias}_log*"))
    regular = [path for path in candidates if path.is_file() and not path.is_symlink()]
    if regular:
        return regular[-1]
    linked = [path for path in candidates if path.is_file()]
    return linked[-1] if linked else None


def normalize_console_logs(run_dir: Path, oeqa_logs_dir: Path) -> list[Path]:
    output_dir = run_dir / "logs/consoles"
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for alias, role in CONSOLE_ALIASES.items():
        source = _console_source(oeqa_logs_dir, alias)
        destination = output_dir / f"{role}.log"
        if source is None or destination.exists():
            continue
        destination.symlink_to(os.path.relpath(source, destination.parent))
        outputs.append(destination)
    return outputs


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def _cpu_observation(primary: str, si_cl0: str, cpu: int) -> JsonObject:
    return {
        "cpu": cpu,
        "oor": bool(
            re.search(rf"CPU{cpu}: Out of Reset \(OoR\) test OK", primary)
        ),
        "online": bool(
            re.search(
                rf"CPU{cpu}: PFDI Online \(OnL\) test \(0 - 40\) OK",
                primary,
            )
        ),
        "monitor_started": (
            f"Started PFDI monitoring for AP cluster 0 core {cpu}" in si_cl0
        ),
        "force_error": bool(
            re.search(rf"CPU{cpu}: injected force error", primary)
        ),
        "sbistc": f"SBISTC_EQ_FAIL_CORE{cpu} detected" in si_cl0,
    }


def _si_cl1_cpu_observation(console: str, cpu: int) -> JsonObject:
    return {
        "cpu": cpu,
        "status_seen": bool(
            re.search(rf"cpu{cpu}.*(?:running|stopped|disabled)", console)
        ),
        "run_success_seen": bool(re.search(rf"cpu{cpu}.*rc=0", console)),
        "success_result_seen": bool(re.search(rf"cpu{cpu}.*SUCCESS", console)),
        "force_error_seen": bool(
            re.search(
                rf"(?:cpu{cpu}.*(?:forced|error-id)|"
                rf"(?:forced|error-id).*cpu{cpu})",
                console,
            )
        ),
        "failed_result_seen": bool(re.search(rf"cpu{cpu}.*FAILED", console)),
    }


def _write_si_cl1_result(run_dir: Path, manifest: JsonObject) -> Path:
    count_value = manifest.get("si_cl1_cpus_count", 4)
    cpu_count = count_value if type(count_value) is int else 4
    console = _read(run_dir / "logs/consoles/si-cl1.log")
    cpu_values: list[JsonValue] = [
        _si_cl1_cpu_observation(console, cpu) for cpu in range(cpu_count)
    ]
    path = run_dir / "results/pfdi-si-cl1.json"
    _write_json_atomic(
        path,
        {
            "schema_version": 1,
            "profile": "pfdi-si-cl1",
            "backend": manifest.get("backend"),
            "machine": manifest.get("machine"),
            "cpu_count": cpu_count,
            "cpus": cpu_values,
            "firmware_info_seen": bool(
                re.search(
                    r"pfdi: cpu0 firmware: (?:stub implementation detected|vendor=)",
                    console,
                )
            ),
        },
    )
    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "si-cl1-pfdi.log").write_text(
        "\n".join(line for line in console.splitlines() if "pfdi" in line.lower())
        + "\n",
        encoding="utf-8",
    )
    return path


def write_profile_result(run_dir: Path, manifest: JsonObject) -> Path | None:
    profile = manifest.get("test_profile")
    if profile == "safety-diagnostics-tests":
        return write_safety_diagnostics_result(run_dir, manifest)
    if profile == "pfdi-si-cl1":
        return _write_si_cl1_result(run_dir, manifest)
    if profile != "pfdi":
        return None
    cpu_count_value = manifest.get("pc_cpus_count_default", 0)
    cpu_count = cpu_count_value if type(cpu_count_value) is int else 0
    primary = _read(run_dir / "logs/consoles/primary.log")
    si_cl0 = _read(run_dir / "logs/consoles/si-cl0.log")
    cpus = [_cpu_observation(primary, si_cl0, cpu) for cpu in range(cpu_count)]
    cpu_values: list[JsonValue] = [cpu for cpu in cpus]
    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    pfdi_lines = [
        line
        for line in primary.splitlines()
        if "Loading config V" in line or "PFDI Online" in line
    ]
    (evidence_dir / "pfdi-sample-app.log").write_text(
        "\n".join(pfdi_lines) + "\n",
        encoding="utf-8",
    )
    module_lines = [
        line
        for line in primary.splitlines()
        if "NEXIOS_BSP_MODULE name=pfdi_misc" in line
        or "PFDI prerequisites OK" in line
    ]
    (evidence_dir / "module-state.txt").write_text(
        "\n".join(module_lines) + "\n",
        encoding="utf-8",
    )
    path = run_dir / "results/pfdi.json"
    _write_json_atomic(
        path,
        {
            "schema_version": 1,
            "profile": "pfdi",
            "backend": manifest.get("backend"),
            "machine": manifest.get("machine"),
            "cpu_count": cpu_count,
            "cpus": cpu_values,
            "fmu_event_count": len(
                re.findall(r"\[FMU\] (?:Non-critical|Critical) fault received:", si_cl0)
            ),
        },
    )
    return path
