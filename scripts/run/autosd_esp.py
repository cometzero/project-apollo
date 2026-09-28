"""Check a stopped VM's private ESP; repair only a proven stale FAT dirty bit.

The caller must supply its private run copy, never the downloaded/source disk,
and must exclude concurrent writers. No general filesystem repair is committed.
"""

import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

try:
    from .autosd_disk import _open_disk, _read, inspect_disk
except ImportError:
    from autosd_disk import _open_disk, _read, inspect_disk


def _flag_offset(boot, size):
    if len(boot) < 512 or boot[510:512] != b"\x55\xaa":
        raise ValueError("Invalid FAT boot signature")
    bps, spc, reserved, fats, roots, total16 = struct.unpack_from("<HBHBHH", boot, 11)
    fat16 = struct.unpack_from("<H", boot, 22)[0]
    total32 = struct.unpack_from("<I", boot, 32)[0]
    total = total16 or total32
    fat_size = fat16 or struct.unpack_from("<I", boot, 36)[0]
    if (bps not in (512, 1024, 2048, 4096) or not spc or spc & (spc - 1)
            or spc > 128 or not reserved or fats not in (1, 2)
            or not total or total * bps > size or not fat_size
            or (total16 and total32)):
        raise ValueError("Invalid FAT BPB/layout")
    data_sectors = total - reserved - fats * fat_size - (roots * 32 + bps - 1) // bps
    clusters = data_sectors // spc
    if 4085 <= clusters < 65525 and fat16 and roots and boot[38] == 0x29:
        if fat_size * bps < (clusters + 2) * 2:
            raise ValueError("FAT16 table too small")
        return 37, "FAT16"
    if (65525 <= clusters < 0x0FFFFFF5 and not fat16 and not roots
            and not total16 and boot[66] == 0x29
            and struct.unpack_from("<H", boot, 42)[0] == 0
            and 2 <= struct.unpack_from("<I", boot, 44)[0] < clusters + 2):
        if fat_size * bps < (clusters + 2) * 4:
            raise ValueError("FAT32 table too small")
        return 65, "FAT32"
    raise ValueError("Unsupported FAT format/layout (expected FAT16 or FAT32)")


def check_private_esp(disk):
    """Return a serializable audit receipt, or fail without repairing the disk.

    fsck works only on an extracted temporary ESP. A write is allowed only when
    its entire proposed repair equals clearing the extended boot state bit 0.
    GPT/ESP bytes and file identity are rechecked immediately before that write.
    """
    tool = shutil.which("fsck.fat")
    if not tool:
        raise ValueError("Missing fsck.fat; install dosfstools to check the private ESP")
    inspected = inspect_disk(disk)
    part = inspected["partitions"]["efi"]
    offset, size = part["offset"], part["size"]
    if offset < 0 or size < 512 or offset + size > inspected["disk_size"]:
        raise ValueError("ESP outside disk bounds")
    with _open_disk(disk) as stream:
        identity = os.fstat(stream.fileno())
        before = _read(stream, offset, size)
    flag, kind = _flag_offset(before[:512], size)
    sha = lambda data: hashlib.sha256(data).hexdigest()
    receipt = {"status": "clean", "fat_type": kind, "esp_offset": offset,
               "esp_size": size, "before_sha256": sha(before), "commands": []}
    with tempfile.TemporaryDirectory(prefix="autosd-esp-") as directory:
        image = Path(directory) / "esp.img"
        image.write_bytes(before)

        def check(option):
            command = [tool, option, str(image)]
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=120, env={**os.environ, "LC_ALL": "C"})
            receipt["commands"].append({"argv": command, "returncode": result.returncode,
                                        "stdout": result.stdout, "stderr": result.stderr})
            return result.returncode

        code = check("-n")
        if code == 0:
            if before[flag] & 1:
                raise ValueError("fsck reported clean but FAT dirty bit remains")
            receipt["after_sha256"] = receipt["before_sha256"]
            return receipt
        if code != 1 or not before[flag] & 1:
            raise ValueError(f"ESP check failed (fsck.fat exit {code}); no disk repair performed")
        if check("-a") not in (0, 1) or check("-n") != 0:
            raise ValueError("ESP does not verify clean after temporary repair")
        after = image.read_bytes()
        expected = bytearray(before)
        expected[flag] &= ~1
        if after != expected:
            raise ValueError("ESP needs repairs beyond the dirty bit; private disk unchanged")
    if inspect_disk(disk) != inspected:
        raise ValueError("Disk metadata changed during ESP check")
    with _open_disk(disk, writable=True) as stream:
        current = os.fstat(stream.fileno())
        if ((current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns)
                != (identity.st_dev, identity.st_ino, identity.st_size, identity.st_mtime_ns)
                or _read(stream, offset, size) != before):
            raise ValueError("Private disk changed during ESP check")
        stream.seek(offset + flag)
        stream.write(after[flag:flag + 1])
        stream.flush()
        os.fsync(stream.fileno())
        if _read(stream, offset, size) != after:
            raise ValueError("ESP dirty-bit write verification failed")
    receipt.update(status="dirty-bit-cleared", flag_offset=flag,
                   after_sha256=sha(after), changed_bytes=1)
    return receipt
