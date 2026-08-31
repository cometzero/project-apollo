from __future__ import annotations

import gzip
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Final, Sequence

try:
    import qbox_apollo_pcie_irq_contract as profile_contract
except ModuleNotFoundError:
    from scripts.test import qbox_apollo_pcie_irq_contract as profile_contract


GUEST_PROBE = profile_contract.GUEST_PROBE
GUEST_WRAPPER = profile_contract.GUEST_WRAPPER
OVERLAY = profile_contract.OVERLAY
Mode = profile_contract.Mode
ProfileError = profile_contract.ProfileError
require_file = profile_contract.require_file
sha256 = profile_contract.sha256

BOOT_PARTITION_OFFSET: Final = 1024 * 1024
UKI_SLOT_A: Final = "::/EFI/Linux/a-slot/auto-ad-nexios-a.efi"
UKI_SLOT_B: Final = "::/EFI/Linux/b-slot/auto-ad-nexios-b.efi"


def run_checked(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    input_data: bytes | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        input=input_data,
        env=env,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ProfileError(f"{Path(command[0]).name}_failed:{detail}")
    return result


def require_tools() -> None:
    tools = ("cp", "cpio", "dtc", "fdtoverlay", "fdtget", "mcopy")
    missing = [tool for tool in tools if shutil.which(tool) is None]
    if missing:
        raise ProfileError("missing_tools:" + ",".join(missing))


def mtools_image(disk: Path) -> str:
    return f"{disk}@@{BOOT_PARTITION_OFFSET}"


def copy_disk(source: Path, destination: Path) -> None:
    run_checked(
        ("cp", "--reflink=auto", "--sparse=always", str(source), str(destination))
    )


def replace_uki(disk: Path, uki: Path) -> None:
    for slot in (UKI_SLOT_A, UKI_SLOT_B):
        run_checked(("mcopy", "-o", "-i", mtools_image(disk), str(uki), slot))


def cpio_entries(root: Path) -> bytes:
    entries = ["."]
    for current, directories, files in os.walk(root, followlinks=False):
        directories.sort()
        files.sort()
        relative = Path(current)
        entries.extend(
            "./" + str((relative / name).relative_to(root)) for name in directories
        )
        entries.extend(
            "./" + str((relative / name).relative_to(root)) for name in files
        )
    return ("\0".join(entries) + "\0").encode()


def build_initramfs(base: Path, output: Path, mode: Mode, input_manifest: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="apollo-pcie-initramfs-") as temporary:
        temp = Path(temporary)
        archive, tree = temp / "base.cpio", temp / "root"
        tree.mkdir()
        with gzip.open(base, "rb") as source, archive.open("wb") as destination:
            shutil.copyfileobj(source, destination)
        with archive.open("rb") as source:
            run_checked(
                (
                    "cpio",
                    "-idmu",
                    "--no-absolute-filenames",
                    "--no-preserve-owner",
                    "--nonmatching",
                    "dev/console",
                ),
                cwd=tree,
                input_data=source.read(),
            )
        installs = {
            tree / "usr/bin/apollo-pcie-its-guest": (GUEST_PROBE, 0o755),
            tree / "usr/bin/qbox-apollo-pcie-irq-test": (GUEST_WRAPPER, 0o755),
            tree / "usr/share/apollo-pcie-its/input-manifest.json": (
                input_manifest,
                0o644,
            ),
        }
        for destination, (source, mode_bits) in installs.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            destination.chmod(mode_bits)
        mode_path = tree / "etc/apollo-pcie-its-mode"
        mode_path.parent.mkdir(parents=True, exist_ok=True)
        mode_path.write_text(mode + "\n", encoding="utf-8")
        init = tree / "init"
        init_text = init.read_text(encoding="utf-8")
        hook = "/usr/bin/qbox-apollo-pcie-irq-test"
        markers = (
            'echo "apollo-qvp login:"',
            "printf 'NEXIOS_BSP_INITRAMFS_READY machine=%s\\n'",
        )
        if hook not in init_text:
            marker = next((value for value in markers if value in init_text), "")
            if not marker:
                raise ProfileError("initramfs_login_marker_missing")
            init_text = init_text.replace(marker, hook + "\n\n" + marker, 1)
        init_text = init_text.replace(
            "if [ -x /usr/bin/apollo-network-setup ]; then",
            "if [ -x /usr/bin/apollo-network-setup ] && "
            "[ ! -x /usr/bin/qbox-apollo-pcie-irq-test ]; then",
            1,
        )
        init.write_text(init_text, encoding="utf-8")
        rebuilt = temp / "test.cpio"
        with rebuilt.open("wb") as destination:
            process = subprocess.run(
                ("cpio", "--null", "-o", "-H", "newc", "--owner=0:0"),
                cwd=tree,
                input=cpio_entries(tree),
                stdout=destination,
                stderr=subprocess.PIPE,
                check=False,
            )
        if process.returncode != 0:
            detail = process.stderr.decode(errors="replace").strip()
            raise ProfileError("cpio_pack_failed:" + detail)
        with rebuilt.open("rb") as source, output.open("wb") as raw:
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0
            ) as compressed:
                shutil.copyfileobj(source, compressed)


def parse_uki_manifest(path: Path) -> tuple[dict[str, Path], list[str]]:
    entries: dict[str, Path] = {}
    command_line = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("CMDLINE="):
            command_line = line.removeprefix("CMDLINE=")
            continue
        fields = line.split(maxsplit=1)
        if len(fields) != 2 or len(fields[0]) != 64:
            continue
        candidate = require_file(Path(fields[1]), "uki_manifest_input")
        if sha256(candidate) != fields[0]:
            raise ProfileError("uki_manifest_hash")
        entries[candidate.name] = candidate
    required = ("Image", "linuxaa64.efi.stub", "os-release", "kernel.release", "ukify")
    if not command_line or any(name not in entries for name in required):
        raise ProfileError("uki_manifest_contract")
    arguments = command_line.split()
    if "pci=nomsi" in arguments:
        raise ProfileError("msix_base_has_pci_nomsi")
    return entries, arguments


def uki_inputs(base_disk: Path) -> tuple[dict[str, Path], list[str]]:
    slot_manifest = require_file(
        base_disk.parent / "auto-ad-nexios-a.efi.manifest", "uki_manifest"
    )
    entries, arguments = parse_uki_manifest(slot_manifest)
    entries["uki_manifest"] = slot_manifest
    return entries, arguments


def build_uki(
    output: Path,
    merged_dtb: Path,
    initramfs: Path,
    inputs: dict[str, Path],
    arguments: list[str],
) -> None:
    tool = inputs["ukify"]
    native_root = tool.parent.parent.parent
    site_packages = next(
        iter(sorted((native_root / "usr/lib").glob("python*/site-packages"))), None
    )
    if site_packages is None:
        raise ProfileError("ukify_pythonpath")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(site_packages)
    run_checked(
        (
            str(tool),
            "build",
            "--efi-arch",
            "aa64",
            f"--linux={inputs['Image']}",
            "--devicetree",
            str(merged_dtb),
            f"--initrd={initramfs}",
            "--stub",
            str(inputs["linuxaa64.efi.stub"]),
            f"--os-release=@{inputs['os-release']}",
            f"--cmdline={' '.join(arguments)}",
            "--uname",
            inputs["kernel.release"].read_text(encoding="utf-8").strip(),
            f"--output={output}",
        ),
        env=environment,
    )


def compile_overlay(base_dtb: Path, output: Path) -> tuple[Path, Path]:
    overlay = output / "apollo-qvp-pcie-irq-overlay.dtbo"
    merged = output / "apollo-qvp-pcie-irq.dtb"
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
    run_checked(("fdtoverlay", "-i", str(base_dtb), "-o", str(merged), str(overlay)))
    run_checked(("dtc", "-I", "dtb", "-O", "dts", "-o", os.devnull, str(merged)))
    its_reg = (
        run_checked(
            (
                "fdtget",
                "-tx",
                str(merged),
                "/soc/interrupt-controller@20800000/msi-controller@20840000",
                "reg",
            )
        )
        .stdout.decode()
        .split()
    )
    if its_reg != ["0", "20840000", "0", "40000"]:
        raise ProfileError("its_translator")
    return overlay, merged
