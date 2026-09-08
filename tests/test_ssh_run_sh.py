from __future__ import annotations

import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/ssh_run.sh"


def test_forwards_script_to_configured_qbox_ssh(tmp_path: Path) -> None:
    guest = tmp_path / "guest.sh"
    guest.write_text("echo guest-test\n", encoding="utf-8")
    fake_ssh = tmp_path / "ssh"
    fake_ssh.write_text(
        "#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$SSH_RUN_ARGS\"\ncat > \"$SSH_RUN_INPUT\"\n",
        encoding="utf-8",
    )
    fake_ssh.chmod(0o755)
    args = tmp_path / "args"
    input_file = tmp_path / "input"
    env = os.environ | {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "QBOX_SSH_HOST": "qbox.test",
        "QBOX_SSH_USER": "guest",
        "QBOX_SSH_PORT": "2200",
        "SSH_RUN_ARGS": str(args),
        "SSH_RUN_INPUT": str(input_file),
    }

    subprocess.run([str(SCRIPT), str(guest)], check=True, env=env)

    assert args.read_text(encoding="utf-8").splitlines()[-5:] == [
        "-p",
        "2200",
        "guest@qbox.test",
        "sh",
        "-s",
    ]
    assert input_file.read_text(encoding="utf-8") == "echo guest-test\n"
