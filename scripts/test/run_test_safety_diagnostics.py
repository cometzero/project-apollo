from __future__ import annotations

import json
from pathlib import Path
import re
from typing import TypeAlias


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def _diagnostic_observation(console: str, name: str) -> JsonObject:
    match = re.search(
        rf"\[INTEGRATION_TEST\]\s+Start:\s*{name}"
        rf"(?P<body>.*?)"
        rf"\[INTEGRATION_TEST\]\s+End:\s*{name}",
        console,
        re.DOTALL,
    )
    body = match.group("body") if match is not None else ""
    summary = re.search(
        r"(?P<total>\d+)\s+Tests\s+"
        r"(?P<failures>\d+)\s+Failures\s+"
        r"(?P<ignored>\d+)\s+Ignored",
        body,
    )
    total = int(summary.group("total")) if summary is not None else 0
    failures = int(summary.group("failures")) if summary is not None else 0
    ignored = int(summary.group("ignored")) if summary is not None else 0
    passed = total - failures - ignored
    success = bool(match is not None and summary is not None and "OK" in body)
    return {
        "started": match is not None,
        "ended": match is not None,
        "total": total,
        "passed": passed,
        "failures": failures,
        "ignored": ignored,
        "result": "PASS" if success and failures == 0 and ignored == 0 else "FAIL",
    }


def write_safety_diagnostics_result(
    run_dir: Path,
    manifest: JsonObject,
) -> Path:
    console = _read(run_dir / "logs/consoles/si-cl0.log")
    diagnostics: JsonObject = {
        name: _diagnostic_observation(console, name) for name in ("ssu", "fmu")
    }
    path = run_dir / "results/safety-diagnostics-tests.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile": "safety-diagnostics-tests",
                "backend": manifest.get("backend"),
                "machine": manifest.get("machine"),
                "diagnostics": diagnostics,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_lines = [
        line
        for line in console.splitlines()
        if "INTEGRATION_TEST" in line
        or re.search(r"\d+ Tests \d+ Failures \d+ Ignored|:PASS|:FAIL|:IGNORE", line)
    ]
    (evidence_dir / "safety-diagnostics.log").write_text(
        "\n".join(evidence_lines) + "\n",
        encoding="utf-8",
    )
    return path
