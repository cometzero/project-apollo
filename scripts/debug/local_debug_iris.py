#!/usr/bin/env python3
"""Set Apollo FVP Iris breakpoints from local debug symbols."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def load_manifest(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def add_iris_python(manifest: dict) -> None:
    iris_python = Path(manifest["iris_python"])
    if not iris_python.is_dir():
        raise SystemExit(f"missing Iris Python path: {iris_python}")
    sys.path.insert(0, str(iris_python))


def resolve_target(model, wanted: str):
    candidates = [wanted]
    if not wanted.startswith("component."):
        candidates.append(f"component.{wanted}")
    for candidate in candidates:
        if candidate in model.instance_infos:
            return model.get_target(candidate)

    suffix_matches = [
        name for name in model.instance_infos if name.endswith(wanted)
    ]
    if len(suffix_matches) == 1:
        return model.get_target(suffix_matches[0])
    if suffix_matches:
        raise SystemExit(
            "ambiguous Iris target for "
            f"{wanted}: {', '.join(sorted(suffix_matches))}"
        )
    raise SystemExit(f"Iris target not found: {wanted}")


def parse_breakpoint(spec: str) -> tuple[str, str | None]:
    if ":" in spec:
        component, symbol = spec.split(":", 1)
        return component, symbol or None
    return spec, None


def symbol_address(component: dict, symbol: str | None) -> tuple[str, int]:
    symbols = component.get("symbols", {})
    if symbol is None:
        symbol = component.get("default_symbol")
    if not symbol:
        raise SystemExit(f"no default symbol for component {component['label']}")
    if symbol not in symbols:
        available = ", ".join(sorted(symbols)) or "none"
        raise SystemExit(
            f"symbol {symbol} not found for {component['label']}; "
            f"available: {available}"
        )
    address = int(symbols[symbol], 16)
    if component.get("arch") == "arm":
        address &= ~1
    return symbol, address


def list_targets(model) -> None:
    for info in model.get_target_info():
        if info.executes_software:
            print(
                f"{info.instance_name}\t{info.component_type}\t"
                f"{info.target_name}\t{info.description}"
            )


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "build/local-apollo-fvp/debug/symbols.json",
    )
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=7100)
    parser.add_argument(
        "--break",
        dest="breakpoints",
        action="append",
        default=[],
        metavar="COMPONENT[:SYMBOL]",
        help="Set a program breakpoint using a component from symbols.json.",
    )
    parser.add_argument(
        "--memory-space",
        default=None,
        help="Optional Iris memory space name for breakpoints.",
    )
    parser.add_argument("--run", action="store_true", help="Run after setting breakpoints.")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--list-targets", action="store_true")
    parser.add_argument("--shutdown", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    add_iris_python(manifest)

    from iris.debug import Model  # pylint: disable=import-error,import-outside-toplevel
    from iris.debug.Exceptions import TimeoutError  # pylint: disable=import-error,import-outside-toplevel

    model = Model.NewNetworkModel(
        args.host,
        args.port,
        timeoutInMs=max(1000, int(args.timeout * 1000)),
        synchronous=False,
    )
    try:
        if args.list_targets:
            list_targets(model)

        installed = []
        components = manifest.get("components", {})
        for spec in args.breakpoints:
            component_name, symbol_name = parse_breakpoint(spec)
            if component_name not in components:
                available = ", ".join(sorted(components))
                raise SystemExit(
                    f"unknown component {component_name}; available: {available}"
                )
            component = components[component_name]
            symbol, address = symbol_address(component, symbol_name)
            target = resolve_target(model, component["target"])
            bpt = target.add_bpt_prog(address, memory_space=args.memory_space)
            installed.append((component_name, symbol, address, target.instance_name, bpt))
            print(
                "breakpoint_set "
                f"component={component_name} symbol={symbol} "
                f"address=0x{address:x} target={target.instance_name} "
                f"id={bpt.number}"
            )

        if args.run:
            print(f"running model with timeout={args.timeout}s")
            try:
                hits = model.run(blocking=True, timeout=args.timeout)
            except TimeoutError:
                model.stop(timeout=5)
                print("breakpoint_timeout")
                return 2
            if not hits:
                print("model_stopped_without_breakpoint")
                return 3
            for hit in hits:
                match = next(
                    (
                        item
                        for item in installed
                        if item[4].number == hit.number
                        and item[3] == hit.target.instance_name
                    ),
                    None,
                )
                if match:
                    component_name, symbol, address, target_name, _ = match
                    print(
                        "breakpoint_hit "
                        f"component={component_name} symbol={symbol} "
                        f"address=0x{address:x} target={target_name} "
                        f"id={hit.number}"
                    )
                else:
                    print(
                        "breakpoint_hit "
                        f"target={hit.target.instance_name} "
                        f"address=0x{hit.address:x} id={hit.number}"
                    )
        return 0
    finally:
        model.release(shutdown=args.shutdown)


if __name__ == "__main__":
    raise SystemExit(main())
