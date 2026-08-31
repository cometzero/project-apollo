"""Device-tree overlay contract tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from qbox_apollo_pcie_irq_profile_support import ROOT, load_module

BUILDER_PATH = ROOT / "scripts/test/prepare_qbox_apollo_pcie_irq_profile.py"
OVERLAY = (
    ROOT
    / "hsoc-stack/tools/qbox-platform/platforms/apollo/test-profile"
    / "apollo-qvp-pcie-irq-overlay.dtso"
)
TASK9_BASE_DTB = (
    ROOT
    / ".omo/evidence/apollo-gic-its/task-9/remediation-2/base/apollo-qvp.dtb"
)


def run_fdtget(dtb: Path, node: str, property_name: str) -> list[int]:
    result = subprocess.run(
        ["fdtget", "-t", "x", str(dtb), node, property_name],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return [int(cell, 16) for cell in result.stdout.split()]


def compile_and_check_irq_overlay(source: Path, base: Path, output_dir: Path) -> None:
    builder = load_module(BUILDER_PATH, "qbox_profile_gic_symbol")
    symbolized_base = output_dir / "base-with-gic-symbol.dtb"
    try:
        builder.prepare_gic_symbol_base(base, symbolized_base)
    except builder.ProfileError as error:
        raise AssertionError(str(error)) from error
    overlay = output_dir / "pcie-irq.dtbo"
    merged = output_dir / "pcie-irq.dtb"
    compile_result = subprocess.run(
        ["dtc", "-@", "-I", "dts", "-O", "dtb", "-o", str(overlay), str(source)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert compile_result.returncode == 0, compile_result.stderr
    assert "Warning" not in compile_result.stderr, compile_result.stderr
    apply_result = subprocess.run(
        ["fdtoverlay", "-i", str(symbolized_base), "-o", str(merged), str(overlay)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert apply_result.returncode == 0, apply_result.stderr
    decompile_result = subprocess.run(
        ["dtc", "-I", "dtb", "-O", "dts", str(merged)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert decompile_result.returncode == 0, decompile_result.stderr
    assert "Bad phandle" not in decompile_result.stderr
    assert "interrupt-controller@20800000" in decompile_result.stdout
    assert "pcie@43b50000" in decompile_result.stdout
    gic_path = "/soc/interrupt-controller@20800000"
    pcie_path = "/soc/pcie@43b50000"
    gic_phandle = run_fdtget(merged, gic_path, "phandle")
    assert gic_phandle == [1]
    assert run_fdtget(merged, gic_path, "#address-cells") == [2]
    assert run_fdtget(merged, gic_path, "#interrupt-cells") == [3]
    interrupt_map = run_fdtget(merged, pcie_path, "interrupt-map")
    assert len(interrupt_map) == 40
    for pin, spi in enumerate((301, 302, 303, 300), start=1):
        entry = interrupt_map[(pin - 1) * 10 : pin * 10]
        assert entry == [0x800, 0, 0, pin, gic_phandle[0], 0, 0, 0, spi, 4]
    gpex_input_301_intid = interrupt_map[8] + 32
    assert gpex_input_301_intid == 333


def test_overlay_maps_only_the_opt_in_endpoint() -> None:
    overlay = OVERLAY.read_text(encoding="utf-8")
    assert "msi-map = <0x8 &pcie_irq_its 0x8 0x1>;" in overlay
    assert "iommu-map = <0x8 &pcie_irq_smmu 0x40 0x1>;" in overlay
    assert "0x12d" in overlay


def test_irq_overlay_is_warning_clean_and_gic_bound(tmp_path: Path) -> None:
    assert TASK9_BASE_DTB.is_file()
    compile_and_check_irq_overlay(OVERLAY, TASK9_BASE_DTB, tmp_path)


@pytest.mark.parametrize(
    ("old", "new"), [("&gic", "&"), ("&gic", "&missing_gic"), ("&gic", "0x1")]
)
def test_irq_overlay_rejects_invalid_gic_bindings(
    tmp_path: Path, old: str, new: str
) -> None:
    source = OVERLAY.read_text(encoding="utf-8")
    assert old in source
    mutated = tmp_path / "mutated.dtso"
    mutated.write_text(source.replace(old, new), encoding="utf-8")
    with pytest.raises(AssertionError):
        compile_and_check_irq_overlay(mutated, TASK9_BASE_DTB, tmp_path)


def test_irq_overlay_rejects_stale_base_dtb(tmp_path: Path) -> None:
    stale_source = tmp_path / "stale-base.dts"
    stale_source.write_text(
        "/dts-v1/;\n/ { #address-cells = <2>; #size-cells = <2>; "
        "soc { #address-cells = <2>; #size-cells = <2>; ranges; }; };\n",
        encoding="utf-8",
    )
    stale_base = tmp_path / "stale-base.dtb"
    subprocess.run(
        ["dtc", "-I", "dts", "-O", "dtb", "-o", str(stale_base), str(stale_source)],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    with pytest.raises(AssertionError):
        compile_and_check_irq_overlay(OVERLAY, stale_base, tmp_path)


@pytest.mark.parametrize(
    ("node", "property_name", "value", "reason"),
    [
        (
            "/soc/interrupt-controller@20800000",
            "#interrupt-cells",
            "2",
            "base_gic_interrupt_cells",
        ),
        ("/soc", "phandle", "1", "base_dtb_invalid"),
    ],
)
def test_gic_symbol_base_rejects_invalid_gic_contract(
    tmp_path: Path, node: str, property_name: str, value: str, reason: str
) -> None:
    builder = load_module(BUILDER_PATH, f"qbox_profile_invalid_{property_name}")
    base = tmp_path / "invalid-base.dtb"
    base.write_bytes(TASK9_BASE_DTB.read_bytes())
    subprocess.run(
        ["fdtput", "-p", "-t", "x", str(base), node, property_name, value],
        check=True,
        capture_output=True,
    )
    with pytest.raises(builder.ProfileError, match=reason):
        builder.prepare_gic_symbol_base(base, tmp_path / "symbolized.dtb")


def test_gic_symbol_base_rejects_conflicting_symbol(tmp_path: Path) -> None:
    builder = load_module(BUILDER_PATH, "qbox_profile_conflicting_symbol")
    base = tmp_path / "conflicting-base.dtb"
    base.write_bytes(TASK9_BASE_DTB.read_bytes())
    subprocess.run(
        [
            "fdtput",
            "-p",
            "-t",
            "s",
            str(base),
            "/__symbols__",
            "gic",
            "/soc/not-the-gic",
        ],
        check=True,
        capture_output=True,
    )
    with pytest.raises(builder.ProfileError, match="base_gic_symbol_conflict"):
        builder.prepare_gic_symbol_base(base, tmp_path / "symbolized.dtb")
