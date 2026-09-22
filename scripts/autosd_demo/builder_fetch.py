#!/usr/bin/env python3
"""Retrieve completed AIB output from the isolated localhost:2226 builder."""
import hashlib
import json
from pathlib import Path
import shutil
import paramiko


def main():
    dest = Path(__file__).resolve().parents[2] / "build/autosd/demo-builder-fullsystem"
    names = ("minimal_qm.osbuild.json", "minimal_qm.aarch64.qcow2")
    if any((dest / name).exists() for name in names):
        raise SystemExit("Refusing to overwrite previously retrieved output")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("127.0.0.1", port=2226, username="root", password="password",
                   allow_agent=False, look_for_keys=False, timeout=20)
    metadata = {}
    try:
        with client.open_sftp() as sftp:
            for name in names:
                source = "/srv/aib/work/" + name
                size = sftp.stat(source).st_size
                if shutil.disk_usage(dest).free < size + 1024**3:
                    raise RuntimeError("Insufficient host free space to retrieve image")
                target = dest / name
                sftp.get(source, str(target))
                with target.open("rb") as stream:
                    digest = hashlib.file_digest(stream, "sha256").hexdigest()
                _, output, errors = client.exec_command("sha256sum " + source, timeout=300)
                remote_digest = output.read().decode().split()[0]
                if output.channel.recv_exit_status() != 0 or digest != remote_digest:
                    raise RuntimeError("Guest/host SHA256 mismatch: " + name)
                metadata[name] = {"size": size, "sha256": digest, "guest_sha256": remote_digest, "verified": True}
                print(name, digest, flush=True)
        (dest / "sha256.json").write_text(json.dumps(metadata, indent=2) + "\n")
    finally:
        client.close()


if __name__ == "__main__":
    main()
