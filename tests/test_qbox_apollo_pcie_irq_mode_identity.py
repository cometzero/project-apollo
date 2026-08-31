from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/test/validate_qbox_apollo_pcie_irq_runtime.py"


def load_validator(name: str):
    spec = importlib.util.spec_from_file_location(name, VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_newc(path: Path, members: dict[str, bytes] | list[tuple[str, bytes]]) -> None:
    archive = bytearray()
    entries = list(members.items()) if isinstance(members, dict) else members
    for inode, (name, data) in enumerate(entries, 1):
        encoded_name = name.encode() + b"\0"
        fields = (
            inode,
            0o100644,
            0,
            0,
            1,
            0,
            len(data),
            0,
            0,
            0,
            0,
            len(encoded_name),
            0,
        )
        archive.extend(
            b"070701" + b"".join(f"{value:08x}".encode() for value in fields)
        )
        archive.extend(encoded_name)
        archive.extend(b"\0" * (-len(archive) % 4))
        archive.extend(data)
        archive.extend(b"\0" * (-len(archive) % 4))
    trailer = b"TRAILER!!!\0"
    fields = (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, len(trailer), 0)
    archive.extend(b"070701" + b"".join(f"{value:08x}".encode() for value in fields))
    archive.extend(trailer)
    archive.extend(b"\0" * (-len(archive) % 4))
    path.write_bytes(gzip.compress(bytes(archive), mtime=0))


def write_pe(path: Path, sections: dict[str, bytes] | list[tuple[str, bytes]]) -> None:
    entries = list(sections.items()) if isinstance(sections, dict) else sections
    pe_offset = 0x80
    optional_size = 0xF0
    table_offset = pe_offset + 24 + optional_size
    raw_offset = (table_offset + len(entries) * 40 + 0x1FF) & ~0x1FF
    raw_sizes = [(len(data) + 0x1FF) & ~0x1FF for _name, data in entries]
    image = bytearray(raw_offset + sum(raw_sizes))
    image[0:2] = b"MZ"
    struct.pack_into("<I", image, 0x3C, pe_offset)
    image[pe_offset : pe_offset + 4] = b"PE\0\0"
    struct.pack_into(
        "<HHIIIHH",
        image,
        pe_offset + 4,
        0xAA64,
        len(entries),
        0,
        0,
        0,
        optional_size,
        0,
    )
    optional = pe_offset + 24
    struct.pack_into("<H", image, optional, 0x20B)
    struct.pack_into("<II", image, optional + 32, 0x1000, 0x200)
    struct.pack_into("<I", image, optional + 60, raw_offset)
    cursor = raw_offset
    for index, (name, data) in enumerate(entries):
        header = table_offset + index * 40
        image[header : header + 8] = name.encode().ljust(8, b"\0")
        struct.pack_into(
            "<IIII", image, header + 8, len(data), 0, raw_sizes[index], cursor
        )
        image[cursor : cursor + len(data)] = data
        cursor += raw_sizes[index]
    path.write_bytes(image)


def write_fat_disk(path: Path, uki: Path) -> None:
    path.write_bytes(b"\0" * (4 * 1024 * 1024))
    subprocess.run(
        ["mkfs.vfat", "--invariant", "--offset=2048", str(path), "3072"],
        check=True,
        capture_output=True,
    )
    image = f"{path}@@1048576"
    for directory in ("EFI", "EFI/Linux", "EFI/Linux/a-slot", "EFI/Linux/b-slot"):
        subprocess.run(
            ["mmd", "-i", image, f"::/{directory}"], check=True, capture_output=True
        )
    for slot in ("a", "b"):
        destination = f"::/EFI/Linux/{slot}-slot/auto-ad-nexios-{slot}.efi"
        subprocess.run(
            ["mcopy", "-i", image, str(uki), destination],
            check=True,
            capture_output=True,
        )


@pytest.mark.parametrize("role", ["input_manifest", "disk", "uki", "initramfs"])
def test_mode_identity_rejects_each_identical_artifact(role: str) -> None:
    validator = load_validator(f"qbox_identity_{role}")
    artifacts = {
        f"{mode}_{name}": {
            "path": f"/profile/{mode}-{name}",
            "size": 1,
            "sha256": hashlib.sha256(f"{mode}-{name}".encode()).hexdigest(),
        }
        for mode in ("msix", "intx")
        for name in ("input_manifest", "disk", "uki", "initramfs")
    }
    artifacts[f"intx_{role}"]["sha256"] = artifacts[f"msix_{role}"]["sha256"]
    with pytest.raises(RuntimeError, match="mode_identity"):
        validator.validate_distinct_mode_artifacts(artifacts)


def test_mode_payload_rejects_swapped_manifest_uki_and_initramfs(
    tmp_path: Path,
) -> None:
    validator = load_validator("qbox_mode_payload")
    dtb = tmp_path / "profile.dtb"
    dtb.write_bytes(b"dtb-contract")
    guest_probe = tmp_path / "guest-probe"
    guest_wrapper = tmp_path / "guest-wrapper"
    guest_probe.write_bytes(b"guest")
    guest_wrapper.write_bytes(b"wrapper")
    manifests: dict[str, Path] = {}
    initramfs: dict[str, Path] = {}
    ukis: dict[str, Path] = {}
    arguments = {
        "msix": ["console=ttyAMA0"],
        "intx": ["console=ttyAMA0", "pci=nomsi"],
    }
    for mode in ("msix", "intx"):
        manifest = tmp_path / f"{mode}.json"
        manifest.write_text(json.dumps({"mode": mode}), encoding="utf-8")
        manifests[mode] = manifest
        archive = tmp_path / f"{mode}.cpio.gz"
        write_newc(
            archive,
            {
                "etc/apollo-pcie-its-mode": f"{mode}\n".encode(),
                "usr/share/apollo-pcie-its/input-manifest.json": manifest.read_bytes(),
                "usr/bin/apollo-pcie-its-guest": guest_probe.read_bytes(),
                "usr/bin/qbox-apollo-pcie-irq-test": guest_wrapper.read_bytes(),
            },
        )
        initramfs[mode] = archive
        uki = tmp_path / f"{mode}.efi"
        write_pe(
            uki,
            {
                ".cmdline": " ".join(arguments[mode]).encode(),
                ".dtb": dtb.read_bytes(),
                ".initrd": archive.read_bytes(),
            },
        )
        ukis[mode] = uki
    validator.validate_mode_payload(
        "msix",
        manifests["msix"],
        ukis["msix"],
        initramfs["msix"],
        dtb,
        arguments["msix"],
        guest_probe,
        guest_wrapper,
    )
    for manifest, uki, archive in (
        (manifests["intx"], ukis["msix"], initramfs["msix"]),
        (manifests["msix"], ukis["intx"], initramfs["msix"]),
        (manifests["msix"], ukis["msix"], initramfs["intx"]),
    ):
        with pytest.raises(RuntimeError, match="mode_identity"):
            validator.validate_mode_payload(
                "msix",
                manifest,
                uki,
                archive,
                dtb,
                arguments["msix"],
                guest_probe,
                guest_wrapper,
            )


def test_mode_disk_rejects_swapped_uki(tmp_path: Path) -> None:
    validator = load_validator("qbox_mode_disk")
    msix_uki = tmp_path / "msix.efi"
    intx_uki = tmp_path / "intx.efi"
    msix_uki.write_bytes(b"msix-uki")
    intx_uki.write_bytes(b"intx-uki")
    disk = tmp_path / "disk.img"
    write_fat_disk(disk, msix_uki)
    validator.validate_disk_slots(disk, msix_uki)
    with pytest.raises(RuntimeError, match="mode_identity"):
        validator.validate_disk_slots(disk, intx_uki)
