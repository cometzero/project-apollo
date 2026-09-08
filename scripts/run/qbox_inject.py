#!/usr/bin/env python3
"""Submit and inspect runtime faults through the existing QBox Monitor."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "test"))
from qbox_runtime_injection_support import (  # noqa: E402
    ApiClient, HttpRequest, RuntimeFailure, ScenarioError, parse_json_object,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monitor", default="http://127.0.0.1:18080")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("capabilities")
    commands.add_parser("list")
    inject = commands.add_parser("inject")
    inject.add_argument("--file", type=Path, required=True)
    for name in ("status", "cancel"):
        commands.add_parser(name).add_argument("id", type=int)
    args = parser.parse_args(argv)
    method, endpoint, payload = "GET", "/api/v1/injections", None
    try:
        if args.command == "capabilities":
            endpoint = "/api/v1/injection-capabilities"
        elif args.command == "inject":
            method = "POST"
            payload = parse_json_object(args.file.read_text(), str(args.file))
        elif args.command in ("status", "cancel"):
            if args.id < 1:
                parser.error("id must be positive")
            endpoint += f"/{args.id}"
            if args.command == "cancel":
                method = "DELETE"
        response = ApiClient(args.monitor.rstrip("/")).request(
            HttpRequest(method, endpoint, payload)
        )
        print(json.dumps(response.body, indent=2))
        return 0 if 200 <= response.status < 300 else 1
    except (OSError, RuntimeFailure, ScenarioError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
