#!/usr/bin/env python3
"""Fetch OTA base evidence or stream a built update directly between private VMs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import paramiko

OUT = Path(__file__).resolve().parents[2] / "build/autosd/demo-ota-followup"


def connect(port):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("127.0.0.1", port=port, username="root", password="password",
                   allow_agent=False, look_for_keys=False, timeout=20)
    return client


def remote_sha(client, path):
    _, output, _ = client.exec_command("sha256sum " + path, timeout=600)
    digest = output.read().decode().split()[0]
    if output.channel.recv_exit_status():
        raise RuntimeError("Remote SHA calculation failed")
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("variant", choices=("base", "good", "bad"))
    parser.add_argument("--target-port", type=int, default=2228)
    args = parser.parse_args()
    with connect(2226) as builder, builder.open_sftp() as source:
        if args.variant == "base":
            metadata = {}
            for name in ("base.qcow2", "base.osbuild.json"):
                path = "/srv/aib/ota/work/" + name
                destination = OUT / name
                if destination.exists():
                    raise ValueError("Refusing to overwrite fetched output")
                size = source.stat(path).st_size
                if shutil.disk_usage(OUT).free < size + 8 * 1024**3:
                    raise ValueError("Host disk reserve would fall below 8 GiB")
                with source.open(path, "rb") as incoming, destination.open("xb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing, 1024**2)
                with destination.open("rb") as stream:
                    digest = hashlib.file_digest(stream, "sha256").hexdigest()
                if digest != remote_sha(builder, path):
                    raise ValueError("Fetched artifact hash mismatch")
                metadata[name] = {"sha256": digest, "size": size}
        else:
            path = f"/srv/aib/ota/work/{args.variant}.oci.tar"
            destination = f"/var/tmp/apollo-ota-{args.variant}.oci.tar"
            size = source.stat(path).st_size
            digest = hashlib.sha256()
            with connect(args.target_port) as target, target.open_sftp() as sink:
                with source.open(path, "rb") as incoming, sink.open(destination, "wx") as outgoing:
                    outgoing.set_pipelined(True)
                    while data := incoming.read(1024**2):
                        outgoing.write(data)
                        digest.update(data)
                value = digest.hexdigest()
                if value != remote_sha(builder, path) or value != remote_sha(target, destination):
                    raise ValueError("Builder/stream/target archive hash mismatch")
            metadata = {args.variant: {"sha256": value, "size": size, "target": destination}}
        (OUT / f"transfer-{args.variant}.json").write_text(json.dumps(metadata, indent=2) + "\n")
        print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
