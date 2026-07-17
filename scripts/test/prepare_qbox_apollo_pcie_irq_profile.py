#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
DESCRIPTION = "Build opt-in Apollo QBox PCIe MSI-X and INTx boot profiles."
OVERLAY = (
    ROOT
    / "hsoc-stack/tools/qbox-platform/platforms/apollo/test-profile"
    / "apollo-qvp-pcie-irq-overlay.dtso"
)
GUEST_TEST = (
    ROOT
    / "hsoc-stack/tools/qbox-platform/platforms/apollo/test-profile"
    / "apollo-qvp-pcie-irq-test.sh"
)
DEFAULT_DEPLOY = ROOT / "build/local-apollo-qvp/deploy/boot"
DEFAULT_OUT = ROOT / "build/qbox-apollo-fvp/pcie-irq-profile"
BOOT_PARTITION_OFFSET = 1024 * 1024
BOOT_DTB = "::/apollo-qvp.dtb"
BOOT_INITRAMFS = "::/initramfs.cpio.gz"
BOOT_SCRIPT = "::/boot.scr"


def run_checked(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    input_data: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"{Path(command[0]).name}_failed:{stderr}")
    return result


def require_tools() -> None:
    missing = [
        tool
        for tool in (
            "cp",
            "cpio",
            "dtc",
            "dumpimage",
            "fdtoverlay",
            "mcopy",
            "mkimage",
        )
        if shutil.which(tool) is None
    ]
    if missing:
        raise RuntimeError("missing_tools:" + ",".join(missing))


def append_bootarg(script: str, argument: str) -> str:
    lines: list[str] = []
    patched = False
    prefix_re = re.compile(r"^(?P<prefix>\s*setenv\s+bootargs\s+)(?P<value>.*)$")
    for original in script.splitlines(keepends=True):
        line = original.rstrip("\r\n")
        newline = original[len(line) :]
        match = prefix_re.match(line)
        if patched or match is None:
            lines.append(original)
            continue

        value = match.group("value").strip()
        quote = ""
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            quote = value[0]
            value = value[1:-1]
        tokens = value.split()
        if argument not in tokens:
            tokens.append(argument)
        lines.append(
            match.group("prefix") + quote + " ".join(tokens) + quote + newline
        )
        patched = True

    if not patched:
        raise RuntimeError("uboot_script_missing_bootargs")
    return "".join(lines)


def mtools_image(disk: Path) -> str:
    return f"{disk}@@{BOOT_PARTITION_OFFSET}"


def copy_disk(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run_checked(
        (
            "cp",
            "--reflink=auto",
            "--sparse=always",
            "--preserve=mode,timestamps",
            str(source),
            str(destination),
        )
    )


def replace_boot_file(disk: Path, source: Path, destination: str) -> None:
    run_checked(
        ("mcopy", "-o", "-i", mtools_image(disk), str(source), destination)
    )


def cpio_entries(root: Path) -> bytes:
    entries = ["."]
    for current, directories, files in os.walk(root, followlinks=False):
        directories.sort()
        files.sort()
        current_path = Path(current)
        for name in directories:
            entries.append("./" + str((current_path / name).relative_to(root)))
        for name in files:
            entries.append("./" + str((current_path / name).relative_to(root)))
    return ("\0".join(entries) + "\0").encode()


def build_test_initramfs(base: Path, output: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="apollo-pcie-initramfs-") as temp:
        temp_dir = Path(temp)
        archive = temp_dir / "base.cpio"
        tree = temp_dir / "root"
        tree.mkdir()

        with gzip.open(base, "rb") as source, archive.open("wb") as destination:
            shutil.copyfileobj(source, destination)
        with archive.open("rb") as source:
            result = subprocess.run(
                (
                    "cpio",
                    "-idmu",
                    "--no-absolute-filenames",
                    "--no-preserve-owner",
                    "--nonmatching",
                    "dev/console",
                ),
                cwd=tree,
                stdin=source,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        if result.returncode != 0:
            raise RuntimeError(
                "cpio_extract_failed:"
                + result.stderr.decode("utf-8", errors="replace").strip()
            )

        guest_destination = tree / "usr/bin/qbox-apollo-pcie-irq-test"
        guest_destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(GUEST_TEST, guest_destination)
        guest_destination.chmod(0o755)

        init = tree / "init"
        init_text = init.read_text(encoding="utf-8")
        hook = "/usr/bin/qbox-apollo-pcie-irq-test"
        marker = 'echo "apollo-qvp login:"'
        if hook not in init_text:
            if marker not in init_text:
                raise RuntimeError("initramfs_login_marker_missing")
            init_text = init_text.replace(marker, hook + "\n\n" + marker, 1)

        network_guard = 'if [ -x /usr/bin/apollo-network-setup ]; then'
        test_network_guard = (
            'if [ -x /usr/bin/apollo-network-setup ] && '
            '[ ! -x /usr/bin/qbox-apollo-pcie-irq-test ]; then'
        )
        if network_guard in init_text:
            init_text = init_text.replace(
                network_guard,
                test_network_guard,
                1,
            )
        init.write_text(init_text, encoding="utf-8")

        rebuilt = temp_dir / "test.cpio"
        with rebuilt.open("wb") as destination:
            process = subprocess.Popen(
                ("cpio", "--null", "-o", "-H", "newc", "--owner=0:0"),
                cwd=tree,
                stdin=subprocess.PIPE,
                stdout=destination,
                stderr=subprocess.PIPE,
            )
            _, stderr = process.communicate(cpio_entries(tree))
        if process.returncode != 0:
            raise RuntimeError(
                "cpio_pack_failed:" + stderr.decode("utf-8", errors="replace").strip()
            )

        output.parent.mkdir(parents=True, exist_ok=True)
        with rebuilt.open("rb") as source, output.open("wb") as raw_output:
            with gzip.GzipFile(
                filename="",
                mode="wb",
                fileobj=raw_output,
                compresslevel=9,
                mtime=0,
            ) as compressed:
                shutil.copyfileobj(source, compressed)


def patch_intx_boot_script(disk: Path, work_dir: Path) -> None:
    original = work_dir / "boot.scr"
    payload = work_dir / "boot.cmd"
    patched = work_dir / "boot-intx.cmd"
    image = work_dir / "boot-intx.scr"

    run_checked(
        ("mcopy", "-i", mtools_image(disk), BOOT_SCRIPT, str(original))
    )
    run_checked(
        (
            "dumpimage",
            "-T",
            "script",
            "-p",
            "0",
            "-o",
            str(payload),
            str(original),
        )
    )
    patched.write_text(
        append_bootarg(payload.read_text(encoding="utf-8"), "pci=nomsi"),
        encoding="utf-8",
    )
    run_checked(
        (
            "mkimage",
            "-A",
            "arm64",
            "-T",
            "script",
            "-C",
            "none",
            "-n",
            "Apollo QVP PCIe INTx test",
            "-d",
            str(patched),
            str(image),
        )
    )
    replace_boot_file(disk, image, BOOT_SCRIPT)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare(
    base_disk: Path,
    base_dtb: Path,
    base_initramfs: Path,
    output_dir: Path,
) -> Path:
    require_tools()
    for path in (base_disk, base_dtb, base_initramfs, OVERLAY, GUEST_TEST):
        if not path.is_file():
            raise RuntimeError(f"missing_input:{path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    overlay = output_dir / "apollo-qvp-pcie-irq-overlay.dtbo"
    merged_dtb = output_dir / "apollo-qvp-pcie-irq.dtb"
    initramfs = output_dir / "apollo-qvp-pcie-irq-initramfs.cpio.gz"
    msix_disk = output_dir / "apollo-qvp-pcie-msix-disk.img"
    intx_disk = output_dir / "apollo-qvp-pcie-intx-disk.img"

    run_checked(
        (
            "dtc",
            "-@",
            "-Wno-interrupts_property",
            "-Wno-interrupt_map",
            "-I",
            "dts",
            "-O",
            "dtb",
            "-o",
            str(overlay),
            str(OVERLAY),
        )
    )
    run_checked(
        (
            "fdtoverlay",
            "-i",
            str(base_dtb),
            "-o",
            str(merged_dtb),
            str(overlay),
        )
    )
    run_checked(("dtc", "-I", "dtb", "-O", "dts", "-o", os.devnull, str(merged_dtb)))
    build_test_initramfs(base_initramfs, initramfs)

    copy_disk(base_disk, msix_disk)
    replace_boot_file(msix_disk, merged_dtb, BOOT_DTB)
    replace_boot_file(msix_disk, initramfs, BOOT_INITRAMFS)

    copy_disk(msix_disk, intx_disk)
    with tempfile.TemporaryDirectory(
        prefix="apollo-pcie-boot-", dir=output_dir
    ) as temp:
        patch_intx_boot_script(intx_disk, Path(temp))

    artifacts = {
        "overlay": overlay,
        "dtb": merged_dtb,
        "initramfs": initramfs,
        "msix_disk": msix_disk,
        "intx_disk": intx_disk,
    }
    manifest = {
        "schema_version": 1,
        "profile": "apollo-qvp-pcie-irq",
        "inputs": {
            "base_disk": str(base_disk.resolve()),
            "base_dtb": str(base_dtb.resolve()),
            "base_initramfs": str(base_initramfs.resolve()),
        },
        "contract": {
            "bdf": "0000:00:01.0",
            "device_id": 0x0008,
            "stream_id": 0x0040,
            "event_id_base": 0,
            "its_translator": "0x20850040",
            "legacy_intx_spi": 301,
            "affinity_cpu": 0,
        },
        "artifacts": {
            name: {
                "path": str(path.resolve()),
                "size": path.stat().st_size,
                "sha256": sha256(path),
            }
            for name, path in artifacts.items()
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--base-disk",
        type=Path,
        default=DEFAULT_DEPLOY / "apollo-qvp-local-disk.img",
    )
    parser.add_argument(
        "--base-dtb",
        type=Path,
        default=DEFAULT_DEPLOY / "apollo-qvp.dtb",
    )
    parser.add_argument(
        "--base-initramfs",
        type=Path,
        default=DEFAULT_DEPLOY / "initramfs.cpio.gz",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = prepare(
            args.base_disk.resolve(),
            args.base_dtb.resolve(),
            args.base_initramfs.resolve(),
            args.output_dir.resolve(),
        )
    except RuntimeError as exc:
        print(str(exc))
        return 1
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
