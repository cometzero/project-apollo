"""Enable the optional vMCU peer only in a private unsigned BSP boot image."""

from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile
from typing import Callable

from autosd_uki import inspect_uki


VMCU_BOOTARG = "apollo.vmcu=1"
BSP_SLOT_IMAGES = (
    "::/EFI/Linux/a-slot/auto-ad-nexios-a.efi",
    "::/EFI/Linux/b-slot/auto-ad-nexios-b.efi",
)


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def patch_bsp_uki(source: Path, destination: Path) -> dict[str, object]:
    """Extend .cmdline within its existing PE allocation; never move sections."""
    if source.resolve() == destination.resolve():
        raise ValueError("vMCU UKI source and destination must differ")
    before = inspect_uki(source)  # Also rejects signed images and PCR policies.
    data = bytearray(source.read_bytes())
    section = before["sections"][".cmdline"]
    start, raw_size = section["offset"], section["raw_size"]
    old_args = data[start:start + section["size"]].rstrip(b"\0").decode("utf-8")
    if any(char in old_args for char in "\0\r\n") or "rdinit=/init" not in old_args.split():
        raise ValueError("vMCU adaptation requires the BSP rdinit=/init UKI")
    tokens = [token for token in old_args.split() if not token.startswith("apollo.vmcu=")]
    tokens.append(VMCU_BOOTARG)
    new_args = " ".join(tokens)
    payload = new_args.encode("utf-8") + b"\0"
    if len(payload) > raw_size:
        raise ValueError("vMCU boot argument exceeds existing UKI .cmdline padding")
    if any(data[start + section["size"]:start + raw_size]):
        raise ValueError("vMCU UKI .cmdline padding contains nonzero data")
    data[start:start + raw_size] = payload.ljust(raw_size, b"\0")
    pe = struct.unpack_from("<I", data, 60)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    optional = pe + 24
    for index in range(count):
        header = optional + optional_size + index * 40
        if data[header:header + 8].rstrip(b"\0") == b".cmdline":
            struct.pack_into("<I", data, header + 8, len(payload))
            break
    # Preserve an omitted PE checksum; refresh one if the input uses it.
    checksum_offset = optional + 64
    if struct.unpack_from("<I", data, checksum_offset)[0]:
        struct.pack_into("<I", data, checksum_offset, 0)
        checksum = sum(int.from_bytes(data[i:i + 2], "little")
                       for i in range(0, len(data), 2))
        while checksum >> 16:
            checksum = (checksum & 0xffff) + (checksum >> 16)
        struct.pack_into("<I", data, checksum_offset, (checksum + len(data)) & 0xffffffff)
    destination.write_bytes(data)
    after = inspect_uki(destination)
    for name, original in before["sections"].items():
        actual = after["sections"][name]
        if name != ".cmdline" and actual != original:
            raise ValueError(f"vMCU adaptation changed preserved UKI section {name}")
        if name == ".cmdline" and any(actual[key] != original[key]
                                      for key in ("offset", "raw_size", "rva")):
            raise ValueError("vMCU adaptation moved the UKI .cmdline section")
    if _digest(source) != before["sha256"]:
        raise ValueError("vMCU adaptation modified its source UKI")
    return {"source_sha256": before["sha256"], "sha256": after["sha256"],
            "old_bootargs": old_args, "new_bootargs": new_args,
            "cmdline_raw_size": raw_size, "cmdline_size": len(payload),
            "preserved_sections": {name: section["sha256"]
                                   for name, section in after["sections"].items()
                                   if name != ".cmdline"}}


def prepare_vmcu_rootfs(
    source: Path, directory: Path, *, enabled: bool,
    copy_image: Callable[[Path, Path], None],
    image_location: Callable[[Path], str],
) -> tuple[Path, dict[str, object]]:
    """Patch both known BSP slots; leave other images and disabled runs alone.

    The runtime supplies its existing sparse copy and WIC partition helpers.
    The filename gate avoids interpreting other products' boot policies.
    """
    info: dict[str, object] = {"enabled": enabled, "changed": False}
    if not enabled:
        info["state"] = "disabled"
        return source, info
    if not source.name.startswith("nexios-bsp-initramfs"):
        info["state"] = "skipped_non_bsp_image"
        return source, info
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{source.stem}-vmcu{source.suffix}"
    if destination.resolve() == source.resolve():
        raise RuntimeError("vMCU WIC destination must differ from source")
    source_hash = _digest(source)
    slots = []
    try:
        with tempfile.TemporaryDirectory(prefix=".vmcu-boot-", dir=directory) as temp:
            scratch = Path(temp)
            # Validate both inputs before creating the private image.
            for index, slot in enumerate(BSP_SLOT_IMAGES):
                original, patched = scratch / f"slot-{index}.efi", scratch / f"slot-{index}-vmcu.efi"
                subprocess.run(["mcopy", "-o", "-i", image_location(source), slot, str(original)],
                               check=True, capture_output=True, text=True)
                slot_info = patch_bsp_uki(original, patched)
                slots.append({"path": slot, **slot_info})
            copy_image(source, destination)
            for index, slot in enumerate(BSP_SLOT_IMAGES):
                subprocess.run(["mcopy", "-o", "-i", image_location(destination),
                                str(scratch / f"slot-{index}-vmcu.efi"), slot],
                               check=True, capture_output=True, text=True)
                # Read back from FAT so the recorded hash proves the boot media.
                readback = scratch / f"slot-{index}-readback.efi"
                subprocess.run(["mcopy", "-o", "-i", image_location(destination), slot, str(readback)],
                               check=True, capture_output=True, text=True)
                if _digest(readback) != slots[index]["sha256"]:
                    raise ValueError(f"vMCU WIC readback mismatch: {slot}")
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        raise RuntimeError(f"vmcu_bsp_boot_preparation_failed:{error}") from error
    if _digest(source) != source_hash:
        raise RuntimeError("vMCU adaptation modified the source WIC")
    info.update({"changed": True, "state": "private_bsp_uki_bootarg",
                 "input": str(source), "output": str(destination),
                 "source_sha256": source_hash, "sha256": _digest(destination),
                 "bootarg": VMCU_BOOTARG, "slots": slots})
    return destination, info
