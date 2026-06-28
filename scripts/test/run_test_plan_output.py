#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


def _read_json_object(path: Path) -> JsonObject:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _json_objects(value: JsonValue) -> list[JsonObject]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _str_values(value: JsonValue) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _excluded_item(item: JsonObject) -> JsonObject:
    output = item.copy()
    if not isinstance(output.get("id"), str) and isinstance(output.get("name"), str):
        output["id"] = output["name"]
    return output


def write_excluded(plan_path: Path, out_path: Path) -> int:
    excluded = [_excluded_item(item) for item in _json_objects(_read_json_object(plan_path).get("excluded"))]
    out_path.write_text(json.dumps({"excluded": excluded}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def print_list(plan_path: Path) -> int:
    plan = _read_json_object(plan_path)
    included = plan.get("included", {})
    if isinstance(included, dict):
        for group, tests in included.items():
            print(f"{group}:")
            for test in _str_values(tests):
                print(f"  {test}")
    print("excluded:")
    for item in _json_objects(plan.get("excluded")):
        print(f"  {item.get('name', '')}: {item.get('reason', '')}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render run_test.sh suite plan output.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    excluded = subparsers.add_parser("write-excluded")
    excluded.add_argument("--plan", type=Path, required=True)
    excluded.add_argument("--out", type=Path, required=True)
    excluded.set_defaults(func=run_write_excluded)
    listing = subparsers.add_parser("print-list")
    listing.add_argument("--plan", type=Path, required=True)
    listing.set_defaults(func=run_print_list)
    return parser.parse_args(argv)


def run_write_excluded(args: argparse.Namespace) -> int:
    return write_excluded(args.plan, args.out)


def run_print_list(args: argparse.Namespace) -> int:
    return print_list(args.plan)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
