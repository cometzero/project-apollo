import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/debug/run_local_gdb.py"


def test_manifest_is_required_only_for_gdb_actions(tmp_path: Path) -> None:
    missing = subprocess.run(
        [sys.executable, str(SCRIPT)],
        text=True,
        capture_output=True,
        check=False,
    )
    log = tmp_path / "console.log"
    log.write_text("ready\n", encoding="utf-8")
    wait_only = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--wait-log-marker-only",
            str(log),
            "ready",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert missing.returncode == 2
    assert "--manifest is required" in missing.stderr
    assert wait_only.returncode == 0
