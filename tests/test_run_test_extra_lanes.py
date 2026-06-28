from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_extra_lanes.py"


def test_extra_lanes_dry_run_uses_plan_included_extra(tmp_path: Path) -> None:
    # Given: a plan that excludes the sw-ref-stack unittest lane.
    plan = tmp_path / "plan.json"
    commands = tmp_path / "commands.jsonl"
    plan.write_text(
        json.dumps(
            {
                "included": {
                    "extra": [
                        "extra-static-compileall",
                        "extra-project-pytest",
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    # When: extra lanes are rendered in dry-run mode.
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--run-dir",
            str(tmp_path),
            "--stamp",
            "unit",
            "--commands-file",
            str(commands),
            "--plan",
            str(plan),
            "--dry-run",
            "--skip-runtime",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: only plan-included local extra lanes are recorded.
    assert result.returncode == 0, result.stderr
    names = [
        json.loads(line)["name"]
        for line in commands.read_text(encoding="utf-8").splitlines()
    ]
    assert "extra-static-compileall" in names
    assert "extra-project-pytest" in names
    assert "extra-sw-ref-stack-unittests" not in names
