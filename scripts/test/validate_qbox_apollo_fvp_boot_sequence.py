#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


RSE_MARKERS = {
    "si_cl1_pre_load": "SI CL1 pre load start",
    "si_cl1_image_loaded": "Image 4 loaded from the primary slot",
    "si_cl1_post_load": "SI CL1 post load complete",
    "si_cl0_pre_load": "SI CL0 pre load start",
    "si_cl0_image_loaded": "Image 3 loaded from the primary slot",
    "si_cl0_released": "SI CL0 is released out of reset",
    "ap_power_on": "RSE to SCP SCMI power on AP succeeded",
    "rse_runtime_handoff": "Jumping to the first image slot",
}

REQUIRED_RUNTIME_MARKERS = {
    "rse": "Starting TF-M BL1_1",
    "si_cl0": "[FWK] Module initialization complete!",
    "si_cl1": "Booting Zephyr OS",
    "linux": "Booting Linux on physical CPU",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Apollo QBox boot-sequence wiring and runtime evidence."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--result-json", type=Path)
    parser.add_argument("--log-dir", type=Path)
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def require_contains(errors: list[str], path: Path, text: str, needle: str, label: str) -> None:
    if needle not in text:
        errors.append(f"{path}: missing {label}: {needle}")


def validate_static(root: Path) -> list[str]:
    errors: list[str] = []
    apollo = root / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block"
    si_cl0 = apollo / "si_cl0.lua"
    si_cl1 = apollo / "si_cl1.lua"

    si_cl0_text = read_text(si_cl0)
    si_cl1_text = read_text(si_cl1)

    require_contains(
        errors,
        si_cl0,
        si_cl0_text,
        'power_on_load = apollo_live_cl0 and {bind = "&si_cl0_loader.reset"} or nil;',
        "RSE SI CL0 PPU-to-loader binding",
    )
    require_contains(
        errors,
        si_cl0,
        si_cl0_text,
        'power_on_reset = apollo_live_cl0 and {bind = "&si_cl0_cpu_0.reset"} or nil;',
        "RSE SI CL0 PPU-to-CPU reset binding",
    )
    require_contains(
        errors,
        si_cl1,
        si_cl1_text,
        'power_on_load = apollo_live_cl1 and {bind = "&si_cl1_loader.reset"} or nil;',
        "RSE SI CL1 cluster PPU-to-loader binding",
    )
    require_contains(
        errors,
        si_cl0,
        si_cl0_text,
        "platform.si_cl0_loader = {\n        moduletype = \"loader\";\n        load_at_elaboration = false;",
        "SI CL0 lazy loader",
    )
    require_contains(
        errors,
        si_cl0,
        si_cl0_text,
        'bind = "&si_cl1_cpu_"..i..".reset";',
        "SI CL0-managed SI CL1 core reset binding",
    )
    require_contains(
        errors,
        si_cl0,
        si_cl0_text,
        "initial_power_status = 0x0;",
        "SI CL1 local PPU initial OFF state",
    )
    require_contains(
        errors,
        si_cl0,
        si_cl0_text,
        "start_in_reset = true;",
        "SI CL0 CPU reset hold",
    )
    require_contains(
        errors,
        si_cl0,
        si_cl0_text,
        "reset_power_on = true;",
        "SI CL0 CPU reset release powers CPU",
    )
    require_contains(
        errors,
        si_cl1,
        si_cl1_text,
        "platform.si_cl1_loader = {\n        moduletype = \"loader\";\n        load_at_elaboration = false;",
        "SI CL1 lazy loader",
    )
    require_contains(
        errors,
        si_cl1,
        si_cl1_text,
        "start_in_reset = true;",
        "SI CL1 CPU reset hold",
    )
    require_contains(
        errors,
        si_cl1,
        si_cl1_text,
        "reset_power_on = true;",
        "SI CL1 CPU reset release powers CPU",
    )

    return errors


def load_result(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_log_paths(result: dict[str, Any], log_dir: Path | None) -> list[Path]:
    paths: list[Path] = []
    console_logs = result.get("console_logs")
    if isinstance(console_logs, dict):
        for value in console_logs.values():
            if isinstance(value, str):
                paths.append(Path(value))
    if log_dir is not None:
        paths.extend(sorted(log_dir.glob("*.log")))
        paths.extend(sorted(log_dir.glob("*.txt")))
    return paths


def load_logs(result: dict[str, Any], log_dir: Path | None) -> dict[str, str]:
    logs: dict[str, str] = {}
    for path in candidate_log_paths(result, log_dir):
        if path.exists() and path.is_file():
            logs[str(path)] = read_text(path)
    return logs


def first_index(text: str, marker: str) -> int | None:
    index = text.find(marker)
    return None if index < 0 else index


def require_order(
    errors: list[str],
    text: str,
    first_name: str,
    second_name: str,
) -> None:
    first_marker = RSE_MARKERS[first_name]
    second_marker = RSE_MARKERS[second_name]
    first = first_index(text, first_marker)
    second = first_index(text, second_marker)
    if first is None or second is None:
        errors.append(
            f"runtime RSE log missing order markers: {first_name} -> {second_name}"
        )
        return
    if first >= second:
        errors.append(f"runtime RSE log order violation: {first_name} !< {second_name}")


def validate_runtime(result: dict[str, Any], log_dir: Path | None) -> list[str]:
    errors: list[str] = []
    logs = load_logs(result, log_dir)
    combined = "\n".join(logs.values())
    if not logs:
        return ["runtime validation requested but no log files were found"]

    for name, marker in REQUIRED_RUNTIME_MARKERS.items():
        if marker not in combined:
            errors.append(f"runtime missing {name} marker: {marker}")

    rse_logs = [
        text
        for path, text in logs.items()
        if "rse" in Path(path).name.lower() or "platform" not in Path(path).name.lower()
    ]
    rse_text = "\n".join(text for text in rse_logs if "Starting TF-M BL1_1" in text)
    if not rse_text:
        rse_text = combined

    require_order(errors, rse_text, "si_cl1_pre_load", "si_cl1_image_loaded")
    require_order(errors, rse_text, "si_cl1_image_loaded", "si_cl1_post_load")
    require_order(errors, rse_text, "si_cl0_pre_load", "si_cl0_image_loaded")
    require_order(errors, rse_text, "si_cl0_image_loaded", "si_cl0_released")
    require_order(errors, rse_text, "ap_power_on", "rse_runtime_handoff")

    if result and result.get("passed") is False:
        errors.append(f"runtime result did not pass: {result.get('verdict')}")

    return errors


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    errors = validate_static(root)
    runtime_errors: list[str] = []
    if not args.static_only:
        runtime_errors = validate_runtime(load_result(args.result_json), args.log_dir)
        errors.extend(runtime_errors)

    status = {
        "passed": not errors,
        "static_only": args.static_only,
        "errors": errors,
        "runtime_errors": runtime_errors,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")

    print(json.dumps(status, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
