#!/usr/bin/env python3
"""Probe source and optional binary support for the Apollo Cortex-R82 model."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


class ProbeError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ProbeError(f"missing required file: {path}") from exc


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise ProbeError(f"{label}: missing {needle!r}")


def probe_sources(source_root: Path) -> list[str]:
    root = source_root.resolve()
    checks: list[str] = []

    cpu64 = read_text(root / "tools/qemu/target/arm/tcg/cpu64.c")
    require(cpu64, "aarch64_cortex_r82_initfn", "QEMU CPU model")
    require(cpu64, '"cortex-r82"', "QEMU CPU model")
    checks.append("qemu-cpu-model")

    helper = read_text(root / "tools/qemu/target/arm/helper.c")
    for reg in ("MPUIR_EL2", "PRSELR_EL2", "PRBAR_EL2", "PRLAR_EL2"):
        require(helper, reg, "QEMU AArch64 EL2 MPU sysregs")
    checks.append("qemu-el2-mpu-sysregs")

    cpu_h = read_text(root / "tools/qemu/target/arm/cpu.h")
    ptw_c = read_text(root / "tools/qemu/target/arm/ptw.c")
    for field in (
        "uint64_t *rbar[M_REG_NUM_BANKS]",
        "uint64_t *rlar[M_REG_NUM_BANKS]",
        "uint64_t *hprbar",
        "uint64_t *hprlar",
    ):
        require(cpu_h, field, "QEMU PMSAv8 64-bit storage")
    require(ptw_c, "uint64_t *regime_rbar", "QEMU PMSAv8 64-bit lookup")
    require(ptw_c, "vaddr address", "QEMU PMSAv8 64-bit lookup")
    require(ptw_c, "hwaddr base", "QEMU PMSAv8 64-bit lookup")
    checks.append("qemu-pmsav8-64bit-storage")

    cpu_arm_cmake = read_text(
        root / "tools/qbox/qemu-components/cpu_arm/CMakeLists.txt"
    )
    require(cpu_arm_cmake, "add_subdirectory(cpu_arm_cortex_r82)", "QBox CPU")
    qbox_header = read_text(
        root
        / "tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/include/cortex-r82.h"
    )
    qbox_cmake = read_text(
        root / "tools/qbox/qemu-components/cpu_arm/cpu_arm_cortex_r82/CMakeLists.txt"
    )
    require(qbox_header, "cpu_arm_cortexR82", "QBox CPU")
    require(qbox_header, '"cortex-r82-arm"', "QBox CPU")
    require(qbox_cmake, "gs_create_dymod(cpu_arm_cortexR82)", "QBox CPU")
    checks.append("qbox-cpu-wrapper")

    return checks


def probe_qemu_binary(qemu_system_aarch64: Path) -> str:
    if not qemu_system_aarch64.exists():
        raise ProbeError(f"missing qemu-system-aarch64: {qemu_system_aarch64}")
    proc = subprocess.run(
        [str(qemu_system_aarch64), "-cpu", "help"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        raise ProbeError(
            f"{qemu_system_aarch64} -cpu help failed with {proc.returncode}"
        )
    if "cortex-r82" not in proc.stdout:
        raise ProbeError("qemu-system-aarch64 -cpu help does not list cortex-r82")
    return "qemu-binary-cpu-help"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path.cwd(),
        help="workspace root containing tools/qemu and tools/qbox",
    )
    parser.add_argument(
        "--qemu-system-aarch64",
        type=Path,
        help="optional qemu-system-aarch64 binary to check with '-cpu help'",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checks = probe_sources(args.source_root)
    if args.qemu_system_aarch64:
        checks.append(probe_qemu_binary(args.qemu_system_aarch64))
    for check in checks:
        print(f"PASS {check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
