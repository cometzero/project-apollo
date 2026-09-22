"""Adapt an unsigned Yocto AArch64 UKI to an AutoSD root filesystem.

The kernel and EFI stub are retained; AutoSD supplies initrd and command line.
This intentionally does not preserve or produce a Secure Boot signature.
"""

import hashlib
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _terminate_legacy_lz4(data):
    """Terminate a bare legacy stream before systemd-stub appends cpio data.

    Kernel unlz4 accepts either EOF or a zero-size block as the stream end.
    An EOF-only stream loses that boundary when the stub concatenates initrds.
    Leave existing concatenated archives and unrecognized input untouched.
    """
    magic = 0x184C2102
    if len(data) < 8 or struct.unpack_from("<I", data)[0] != magic:
        return data, False
    # lib/decompress_unlz4.c: 8 MiB uncompressed chunks, LZ4_compressBound.
    max_chunk = (8 << 20) + (8 << 20) // 255 + 16
    offset, blocks = 4, 0
    while offset + 4 <= len(data):
        size = struct.unpack_from("<I", data, offset)[0]
        if size == magic:
            offset += 4
            continue
        if not size or size > max_chunk or offset + 4 + size > len(data):
            return data, False
        offset += 4 + size
        blocks += 1
        if offset == len(data):
            return data + b"\0" * 4, bool(blocks)
    return data, False


def inspect_uki(path):
    """Validate PE bounds and return serializable UKI section metadata."""
    data = Path(path).read_bytes()
    if len(data) < 64 or data[:2] != b"MZ":
        raise ValueError("UKI is not a DOS/PE executable")
    pe = struct.unpack_from("<I", data, 60)[0]
    if pe + 24 > len(data) or data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("Invalid PE header")
    machine, count = struct.unpack_from("<HH", data, pe + 4)
    optsize = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    table = opt + optsize
    if machine != 0xAA64 or optsize < 152 or table + count * 40 > len(data):
        raise ValueError("Expected a complete AArch64 PE32+ image")
    if struct.unpack_from("<H", data, opt)[0] != 0x20B:
        raise ValueError("Expected PE32+ optional header")
    directories = struct.unpack_from("<I", data, opt + 108)[0]
    if directories > (optsize - 112) // 8:
        raise ValueError("PE data directories exceed optional header")
    if directories > 4 and any(struct.unpack_from("<II", data, opt + 144)):
        raise ValueError("Signed UKI cannot be adapted; supply an unsigned UKI")
    image_base = struct.unpack_from("<Q", data, opt + 24)[0]
    alignment = struct.unpack_from("<I", data, opt + 32)[0]
    image_size, headers_size = struct.unpack_from("<II", data, opt + 56)
    if not alignment or alignment & (alignment - 1):
        raise ValueError("Invalid PE section alignment")
    sections = {}
    raw_ranges, virtual_ranges = [], []
    for index in range(count):
        offset = table + index * 40
        name = data[offset:offset + 8].rstrip(b"\0").decode("ascii")
        size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", data, offset + 8)
        if not name or name in sections:
            raise ValueError("Invalid or duplicate PE section name")
        if raw_size and (raw_offset < headers_size or raw_offset + raw_size > len(data)):
            raise ValueError(f"Section {name} exceeds PE file bounds")
        if rva + max(size, raw_size) > image_size:
            raise ValueError(f"Section {name} exceeds PE image bounds")
        for start, end in raw_ranges:
            if raw_size and raw_offset < end and raw_offset + raw_size > start:
                raise ValueError("Overlapping PE file sections")
        for start, end in virtual_ranges:
            if rva < end and rva + max(size, raw_size) > start:
                raise ValueError("Overlapping PE virtual sections")
        if raw_size:
            raw_ranges.append((raw_offset, raw_offset + raw_size))
        virtual_ranges.append((rva, rva + max(size, raw_size)))
        sections[name] = {"size": size, "rva": rva, "raw_size": raw_size,
                          "offset": raw_offset,
                          "sha256": _sha(data[raw_offset:raw_offset + min(size, raw_size)])}
    for name in (".linux", ".initrd", ".cmdline"):
        if name not in sections or not sections[name]["size"]:
            raise ValueError(f"Missing UKI section {name}")
        if sections[name]["size"] > sections[name]["raw_size"]:
            raise ValueError(f"UKI section {name} contains uninitialized data")
    if ".pcrsig" in sections:
        raise ValueError("UKI contains signed PCR policies; adaptation would invalidate them")
    return {"machine": "aarch64", "sha256": _sha(data), "image_base": image_base,
            "section_alignment": alignment, "sections": sections,
            "kernel_sha256": sections[".linux"]["sha256"]}


def _objcopy():
    # GNU objcopy supports explicit PE section VMAs. LLVM versions without
    # --change-section-vma cannot safely grow an initrd followed by .sbat.
    candidates = [shutil.which("aarch64-linux-gnu-objcopy"),
                  "/opt/arm/gcc-linaro-aarch64/bin/aarch64-linux-gnu-objcopy",
                  shutil.which("llvm-objcopy")]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            result = subprocess.run([candidate, "--help"], capture_output=True, text=True)
            if "--change-section-vma" in result.stdout:
                return candidate
    raise ValueError("AArch64 objcopy with --change-section-vma support is required")


def prepare_uki(source, initrd, bootargs, destination):
    """Create an unsigned AutoSD UKI without modifying the source artifact."""
    source, initrd, destination = map(lambda p: Path(p).resolve(),
                                      (source, initrd, destination))
    if destination in (source, initrd):
        raise ValueError("UKI destination must differ from its inputs")
    if not bootargs or any(c in bootargs for c in "\0\r\n"):
        raise ValueError("UKI command line must be a nonempty single line")
    before = inspect_uki(source)
    if not initrd.is_file() or initrd.stat().st_size == 0:
        raise ValueError("AutoSD initrd must be nonempty")
    input_initrd = initrd.read_bytes()
    embedded_initrd, terminator_added = _terminate_legacy_lz4(input_initrd)
    replaced = {".initrd", ".cmdline", ".osrel", ".dtb"}
    alignment = before["section_alignment"]
    end = max(s["rva"] + max(s["size"], s["raw_size"])
              for name, s in before["sections"].items() if name not in replaced)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".autosd-uki-", dir=destination.parent) as tmp:
        tmp = Path(tmp)
        cmdline, osrel, output = tmp / "cmdline", tmp / "osrel", tmp / "adapted.efi"
        normalized_initrd = tmp / "initrd"
        normalized_initrd.write_bytes(embedded_initrd)
        cmdline.write_bytes(bootargs.encode("utf-8") + b"\0")
        osrel.write_bytes(b'ID=autosd\nNAME="AutoSD"\nPRETTY_NAME="AutoSD (Apollo Yocto kernel)"\n')
        command = [_objcopy()]
        for name in sorted(replaced):
            command += ["--remove-section", name]
        for name, payload in ((".osrel", osrel), (".cmdline", cmdline), (".initrd", normalized_initrd)):
            end = (end + alignment - 1) & ~(alignment - 1)
            command += ["--add-section", f"{name}={payload}",
                        "--change-section-vma", f"{name}={before['image_base'] + end:#x}",
                        "--set-section-flags", f"{name}=alloc,load,readonly,data,contents"]
            end += payload.stat().st_size
        subprocess.run(command + [str(source), str(output)], check=True,
                       capture_output=True, text=True)
        after = inspect_uki(output)
        for name, section in before["sections"].items():
            if name not in replaced and after["sections"].get(name, {}).get("sha256") != section["sha256"]:
                raise ValueError(f"UKI adaptation changed preserved section {name}")
        if ".dtb" in after["sections"]:
            raise ValueError("Adapted UKI still overrides firmware DTB")
        if after["sections"][".initrd"]["sha256"] != _sha(embedded_initrd):
            raise ValueError("Adapted UKI initrd differs from prepared AutoSD input")
        if inspect_uki(source)["sha256"] != before["sha256"]:
            raise ValueError("Source UKI changed during adaptation")
        output.replace(destination)
    return {**after, "source": str(source), "destination": str(destination),
            "initrd": str(initrd), "source_sha256": before["sha256"],
            "input_initrd_sha256": _sha(input_initrd),
            "embedded_initrd_sha256": _sha(embedded_initrd),
            "lz4_terminator_added": terminator_added,
            "bootargs": bootargs, "secure_boot": False}
