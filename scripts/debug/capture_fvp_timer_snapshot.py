#!/usr/bin/env python3
"""Capture explicit FVP Iris timer views into schema-v1 JSON evidence."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
from typing import Final


SCRIPT_DIR: Final = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import local_debug_iris
from fvp_secure_frame_access import enabled_secure_frame, enabled_secure_frame_memory
from fvp_timer_specs import SampleSpec, ViewSpec, parse_sample, parse_view


SCHEMA_VERSION: Final = 1
VIEW_DOMAINS: Final = {
    "smd": "css",
    "ap_cpu0": "css",
    "ap_refclk_ns": "css",
    "ap_refclk_s": "css",
    "si0_cpu0": "css",
    "si0_cntbase": "css",
    "si1_cpu0": "css",
    "rse_lsc": "rse",
    "rse_timer0": "rse",
    "rse_timer1": "rse",
    "rse_timer2": "rse",
    "rse_timer3": "rse",
}
SECURE_MMIO_VIEW_ID: Final = "ap_refclk_s"


def revision(root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unavailable"


def read_view(model: object, spec: ViewSpec) -> tuple[int | None, str | None]:
    target = local_debug_iris.resolve_target(model, spec.target)
    try:
        match spec.kind:
            case "register":
                value = target.read_register(spec.value)
            case "memory":
                if spec.address is None or spec.width is None:
                    return None, "memory view has no address or width"
                value = target.read_memory(
                    spec.address,
                    memory_space=spec.memory_space or "SP",
                    size=spec.width,
                    count=1,
                )
                if isinstance(value, bytearray):
                    return int.from_bytes(value, "little"), None
        if isinstance(value, int):
            return value, None
        return None, f"Iris returned {type(value).__name__}, not an integer"
    except (AttributeError, RuntimeError, TypeError, ValueError) as error:
        return None, str(error)


def simulation_time(model: object, fallback_timebase_hz: int) -> tuple[int, int] | None:
    client = getattr(model, "client", None)
    iris_call = getattr(client, "irisCall", None)
    if not callable(iris_call):
        return None
    raw = iris_call().simulationTime_get(instId=1)
    if not isinstance(raw, dict):
        return None
    ticks, tick_hz = raw.get("ticks"), raw.get("tickHz")
    if not isinstance(ticks, int):
        return None
    if not isinstance(tick_hz, int) or tick_hz <= 0:
        tick_hz = fallback_timebase_hz
    return ticks, tick_hz


def new_runnable_model(
    model_api: object,
    host: str,
    port: int,
    timeout_ms: int,
) -> object:
    factory = getattr(model_api, "NewNetworkModel")
    model = factory(
        host,
        port,
        timeoutInMs=timeout_ms,
        synchronous=False,
    )
    if not callable(getattr(model, "run", None)):
        raise RuntimeError("Iris model does not provide run()")
    return model


def add_program_breakpoint(
    target: object,
    address: int,
    memory_space: str | None,
) -> object:
    add_breakpoint = getattr(target, "add_bpt_prog")
    return add_breakpoint(address, memory_space=memory_space)


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=root / "build/local-apollo-fvp/debug/symbols.json"
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=7100)
    parser.add_argument("--machine", default="apollo-fvp")
    parser.add_argument("--sample", action="append", default=[])
    parser.add_argument("--view", action="append", default=[])
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--breakpoint-memory-space")
    parser.add_argument("--iris-timebase-hz", type=int, default=1_000_000_000_000)
    parser.add_argument("--enable-secure-frame", action="store_true")
    parser.add_argument("--secure-access-register")
    parser.add_argument("--secure-access-memory")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    try:
        samples = [parse_sample(item) for item in args.sample]
        views = [parse_view(item) for item in args.view]
    except ValueError as error:
        print(f"invalid snapshot specification: {error}", file=sys.stderr)
        return 2
    if args.iris_timebase_hz <= 0:
        print("--iris-timebase-hz must be positive", file=sys.stderr)
        return 2
    access_specs = (args.secure_access_register, args.secure_access_memory)
    if args.enable_secure_frame and sum(value is not None for value in access_specs) != 1:
        print("--enable-secure-frame requires exactly one secure access spec", file=sys.stderr)
        return 2
    result: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "producer": "fvp",
        "status": "unavailable",
        "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": {
            "machine": args.machine,
            "revision": revision(root),
            "artifact_path": str(args.manifest.resolve()),
        },
        "samples": [],
    }
    if not samples or not views:
        result["reason"] = "samples_and_views_are_required"
    elif not args.manifest.exists():
        result["reason"] = f"missing_manifest:{args.manifest}"
    else:
        manifest = local_debug_iris.load_manifest(args.manifest)
        local_debug_iris.add_iris_python(manifest)
        from iris.debug import Model
        from iris.debug.Exceptions import TimeoutError

        model = new_runnable_model(
            Model,
            args.host,
            args.port,
            max(1000, int(args.timeout * 1000)),
        )
        captured: list[dict[str, object]] = []
        errors: list[str] = []
        try:
            for spec in samples:
                component = manifest.get("components", {}).get(spec.component)
                if not component:
                    errors.append(f"unknown_component:{spec.component}")
                    continue
                _, address = local_debug_iris.symbol_address(component, spec.symbol)
                target = local_debug_iris.resolve_target(model, component["target"])
                breakpoint = add_program_breakpoint(
                    target,
                    address,
                    args.breakpoint_memory_space,
                )
                try:
                    hits = model.run(blocking=True, timeout=args.timeout)
                except TimeoutError:
                    errors.append(f"sample_timeout:{spec.name}")
                    target.remove_bpt(breakpoint.number)
                    continue
                target.remove_bpt(breakpoint.number)
                if not hits:
                    errors.append(f"sample_no_breakpoint:{spec.name}")
                    continue
                time_value = simulation_time(model, args.iris_timebase_hz)
                if time_value is None:
                    errors.append(f"simulation_time_unavailable:{spec.name}")
                    continue
                raw_ticks, iris_timebase_hz = time_value
                sample_time_ns = raw_ticks * 1_000_000_000 // iris_timebase_hz
                sample_views: dict[str, object] = {}
                access_target = None
                access_register = args.secure_access_register
                access_memory = args.secure_access_memory
                if access_register:
                    target_name, separator, access_register = access_register.partition(":")
                    if not separator or not target_name or not access_register:
                        errors.append(f"invalid_secure_access_register:{args.secure_access_register}")
                    else:
                        access_target = local_debug_iris.resolve_target(model, target_name)
                access_context = (
                    enabled_secure_frame(access_target, access_register)
                    if args.enable_secure_frame and access_target is not None
                    else enabled_secure_frame_memory(
                        local_debug_iris.resolve_target(model, access_memory.split(":", 1)[0]),
                        access_memory.split(":", 2)[1],
                        int(access_memory.rsplit(":", 1)[1], 0),
                    )
                    if args.enable_secure_frame and access_memory is not None
                    else contextlib.nullcontext(None)
                )
                with access_context as original_cntacr1:
                    for view in views:
                        counter, error = read_view(model, view)
                        observation: dict[str, object] = {
                            "domain": VIEW_DOMAINS.get(view.view_id, "unspecified"),
                            "observed": counter is not None,
                        }
                        if view.view_id == SECURE_MMIO_VIEW_ID:
                            observation["access_control_state"] = (
                                "enabled" if args.enable_secure_frame else "unknown"
                            )
                            if original_cntacr1 is not None:
                                observation["original_cntacr1"] = original_cntacr1
                        if counter is not None:
                            observation["counter"] = counter
                        if error is not None:
                            observation["error"] = error
                            errors.append(f"view_unavailable:{spec.name}:{view.view_id}:{error}")
                        sample_views[view.view_id] = observation
                captured.append(
                    {
                        "name": spec.name,
                        "marker": f"{spec.component}:{spec.symbol}",
                        "sim_time_ns": sample_time_ns,
                        "raw_simulation_ticks": raw_ticks,
                        "iris_timebase_hz": iris_timebase_hz,
                        "views": sample_views,
                    }
                )
        finally:
            model.release(shutdown=False)
        result["samples"] = captured
        if not errors and len(captured) == len(samples):
            result["status"] = "pass"
        else:
            result["reason"] = errors
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
