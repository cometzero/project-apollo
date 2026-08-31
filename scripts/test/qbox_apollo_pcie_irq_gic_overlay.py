#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# ─── How to run ───
# python3 scripts/test/qbox_apollo_pcie_irq_gic_overlay.py

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from typing import Final

try:
    import qbox_apollo_pcie_irq_contract as profile_contract
except ModuleNotFoundError:
    from scripts.test import qbox_apollo_pcie_irq_contract as profile_contract

ProfileError = profile_contract.ProfileError
sha256 = profile_contract.sha256

GIC_PATH: Final = "/soc/interrupt-controller@20800000"
GIC_PHANDLE: Final = 1
GIC_ADDRESS_CELLS: Final = 2
GIC_INTERRUPT_CELLS: Final = 3


def fdt_cells(dtb: Path, node: str, property_name: str) -> tuple[int, ...]:
    result = subprocess.run(
        ("fdtget", "-t", "x", str(dtb), node, property_name),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ProfileError(f"base_gic_property:{property_name}")
    try:
        return tuple(int(cell, 16) for cell in result.stdout.split())
    except ValueError as error:
        raise ProfileError(f"base_gic_property:{property_name}") from error


def gic_symbol(dtb: Path) -> str | None:
    result = subprocess.run(
        ("fdtget", "-t", "s", str(dtb), "/__symbols__", "gic"),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    if "FDT_ERR_NOTFOUND" not in result.stderr:
        raise ProfileError("base_gic_symbol_read")
    return None


def validate_base_gic(dtb: Path) -> None:
    structural = subprocess.run(
        ("dtc", "-I", "dtb", "-O", "dtb", "-o", os.devnull, str(dtb)),
        capture_output=True,
        text=True,
        check=False,
    )
    if structural.returncode != 0:
        raise ProfileError("base_dtb_invalid")
    if fdt_cells(dtb, GIC_PATH, "phandle") != (GIC_PHANDLE,):
        raise ProfileError("base_gic_phandle")
    if fdt_cells(dtb, GIC_PATH, "#address-cells") != (GIC_ADDRESS_CELLS,):
        raise ProfileError("base_gic_address_cells")
    if fdt_cells(dtb, GIC_PATH, "#interrupt-cells") != (GIC_INTERRUPT_CELLS,):
        raise ProfileError("base_gic_interrupt_cells")
    symbol = gic_symbol(dtb)
    if symbol is not None and symbol != GIC_PATH:
        raise ProfileError("base_gic_symbol_conflict")


def prepare_gic_symbol_base(base: Path, output: Path) -> None:
    if shutil.which("fdtput") is None:
        raise ProfileError("missing_tools:fdtput")
    validate_base_gic(base)
    source_sha256 = sha256(base)
    shutil.copyfile(base, output)
    result = subprocess.run(
        ("fdtput", "-p", "-t", "s", str(output), "/__symbols__", "gic", GIC_PATH),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ProfileError("base_gic_symbol_write")
    validate_base_gic(output)
    if gic_symbol(output) != GIC_PATH:
        raise ProfileError("base_gic_symbol_write")
    if sha256(base) != source_sha256:
        raise ProfileError("base_dtb_modified")


def validate_warning_clean_overlay() -> None:
    overlay = profile_contract.OVERLAY
    result = subprocess.run(
        ("dtc", "-@", "-I", "dts", "-O", "dtb", "-o", os.devnull, str(overlay)),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ProfileError("overlay_dtc_failed:" + result.stderr.strip())
    if result.stderr.strip():
        raise ProfileError("overlay_dtc_warning:" + result.stderr.strip())
