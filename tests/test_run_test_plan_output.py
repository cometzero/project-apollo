from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from run_test_helpers import ROOT


def test_write_excluded_wraps_sidecar_with_f4_ids(tmp_path: Path) -> None:
    # Given: a plan whose excluded tests only carry the legacy name field.
    plan_path = tmp_path / "plan.json"
    out_path = tmp_path / "excluded.json"
    plan_path.write_text(
        json.dumps(
            {
                "excluded": [
                    {
                        "name": "test_40_virtualization",
                        "reason": "excluded_baremetal_no_xen",
                        "source_suite": "TEST_SUITES:demos:virtualization",
                    },
                    {
                        "name": "domu-lifecycle",
                        "reason": "excluded_baremetal_no_xen_domu",
                        "note": "DomU lifecycle requires Xen virtualization.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    # When: the public sidecar writer renders excluded.json.
    result = subprocess.run(
        [
            sys.executable,
            "scripts/test/run_test_plan_output.py",
            "write-excluded",
            "--plan",
            str(plan_path),
            "--out",
            str(out_path),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: F4 can read .excluded[]?.id while legacy fields remain available.
    assert result.returncode == 0, result.stderr
    sidecar = json.loads(out_path.read_text(encoding="utf-8"))
    assert sidecar["excluded"][0]["id"] == "test_40_virtualization"
    assert sidecar["excluded"][0]["name"] == "test_40_virtualization"
    assert sidecar["excluded"][1]["id"] == "domu-lifecycle"
    assert "DomU" in sidecar["excluded"][1]["note"]
