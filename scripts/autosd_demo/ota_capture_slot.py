#!/usr/bin/env python3
"""Read a quiescent guest UKI slot and verify its actual kernel and cmdline.

Run only after bootc staging or boot has completed, never during an update.
This reads the guest block device via SSH; it never writes or mounts it.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from ota_transfer import connect, remote_sha

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/run"))
from autosd_uki import inspect_uki


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slot", choices=("a", "b"))
    parser.add_argument("--port", type=int, default=2228)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expected-kernel", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    device = "/dev/disk/by-partlabel/ukiboot_" + args.slot
    destination = args.out / ("slot-" + args.slot + ".efi")
    total = 0
    maximum = 128 * 1024**2
    with connect(args.port) as client, client.open_sftp() as transfer:
        with transfer.open(device, "rb") as source, destination.open("xb") as output:
            while data := source.read(1024**2):
                total += len(data)
                if total > maximum:
                    raise ValueError("Unexpected slot larger than the AutoSD 128 MiB contract")
                output.write(data)
        if total != maximum:
            raise ValueError("Incomplete AutoSD slot read")
        metadata = inspect_uki(destination)
        if metadata["sha256"] != remote_sha(client, device):
            raise ValueError("Slot changed during capture or transfer checksum mismatch")
    with args.expected_kernel.open("rb") as stream:
        expected = hashlib.file_digest(stream, "sha256").hexdigest()
    if metadata["kernel_sha256"] != expected:
        raise ValueError("Native UKI kernel does not match the expected Apollo Image")
    section = metadata["sections"][".cmdline"]
    with destination.open("rb") as source:
        source.seek(section["offset"])
        cmdline = source.read(section["size"]).rstrip(b"\0").decode()
    metadata.update(slot=args.slot, device=device, cmdline=cmdline,
                    expected_kernel_sha256=expected, status="SLOT_CONTENT_VERIFIED_NOT_OTA_QUALIFICATION")
    (args.out / "inspect.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
