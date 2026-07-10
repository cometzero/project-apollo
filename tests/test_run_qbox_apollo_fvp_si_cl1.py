import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_si_cl1.py"
CONF = ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-si-cl1.lua"


def test_check_only_records_effective_tcg_mode(tmp_path):
    out_dir = tmp_path / "result"
    env = os.environ.copy()
    env["QBOX_APOLLO_SI_CL1_TCG_MODE"] = "MULTI"

    checked = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--check-only",
            "--conf",
            str(CONF),
            "--image",
            str(SCRIPT),
            "--symbols",
            str(SCRIPT),
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert checked.returncode == 0, checked.stderr
    result = json.loads((out_dir / "result.json").read_text(encoding="utf-8"))
    assert result["si_cl1_tcg_mode"] == "MULTI"
    assert "si_cl1_tcg_mode: MULTI" in (out_dir / "summary.txt").read_text(
        encoding="utf-8"
    )
