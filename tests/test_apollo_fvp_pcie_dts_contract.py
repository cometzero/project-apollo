from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Final

import pytest


ROOT: Final = Path(__file__).resolve().parents[1]
TF_A: Final = ROOT / "hsoc-stack/components/primary_compute/trusted-firmware-a"
LINUX: Final = ROOT / "hsoc-stack/components/primary_compute/linux"
PCIE_PATH: Final = "/soc/pcie@10040000000"
EXPECTED_REG: Final = (0x100, 0x40000000, 0, 0x10000000)
EXPECTED_RANGES: Final = (
    0x02000000,
    0,
    0x60000000,
    0,
    0x60000000,
    0,
    0x20000000,
    0x43000000,
    0x101,
    0x60000000,
    0x101,
    0x60000000,
    0,
    0x20000000,
)
EXPECTED_MAP_SUFFIX: Final = (0, 0x10000)


def _run(*command: str) -> str:
    return subprocess.run(
        command,
        check=True,
        cwd=ROOT,
        text=True,
        capture_output=True,
    ).stdout


def _compile(source: Path, output: Path, include_dirs: tuple[Path, ...]) -> Path:
    preprocessed = output.with_suffix(".pre.dts")
    cpp_command = ["cpp", "-undef", "-x", "assembler-with-cpp"]
    for include_dir in include_dirs:
        cpp_command.extend(("-I", str(include_dir)))
    cpp_command.append(str(source))
    preprocessed.write_text(_run(*cpp_command))
    _run(
        "dtc",
        "-Wno-unit_address_vs_reg",
        "-Wno-simple_bus_reg",
        "-Wno-unique_unit_address",
        "-I",
        "dts",
        "-O",
        "dtb",
        "-o",
        str(output),
        str(preprocessed),
    )
    return output


def _cells(dtb: Path, node: str, property_name: str) -> tuple[int, ...]:
    return tuple(
        int(cell, 16)
        for cell in _run(
            "fdtget", "-t", "x", str(dtb), node, property_name
        ).split()
    )


def _string(dtb: Path, node: str, property_name: str) -> str:
    return _run("fdtget", "-t", "s", str(dtb), node, property_name).strip()


@pytest.fixture(scope="module")
def compiled_fvp_dtbs(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    out = tmp_path_factory.mktemp("apollo-fvp-pcie-dts")
    tfa_dtb = _compile(
        TF_A / "fdts/apollo_fvp_fvp.dts",
        out / "tfa-apollo-fvp.dtb",
        (
            TF_A / "include",
            TF_A / "include/arch/aarch64",
            TF_A / "fdts",
            TF_A
            / "plat/arm/board/automotive_rd/platform/apollo_fvp/include",
            TF_A / "plat/arm/board/automotive_rd/include",
        ),
    )
    linux_dtb = _compile(
        LINUX / "arch/arm64/boot/dts/arm/apollo-fvp.dts",
        out / "linux-apollo-fvp.dtb",
        (
            LINUX / "include",
            LINUX / "scripts/dtc/include-prefixes",
            LINUX / "arch/arm64/boot/dts/arm",
        ),
    )
    return tfa_dtb, linux_dtb


def test_aligned_host_contract_when_fvp_dtbs_are_compiled(
    compiled_fvp_dtbs: tuple[Path, Path],
) -> None:
    # Given two independently owned Apollo FVP source trees
    # When each tree is preprocessed and compiled by dtc
    contracts = []
    for dtb in compiled_fvp_dtbs:
        contracts.append(
            (
                _string(dtb, PCIE_PATH, "compatible"),
                _cells(dtb, PCIE_PATH, "reg"),
                _cells(dtb, PCIE_PATH, "ranges"),
                _cells(dtb, PCIE_PATH, "bus-range"),
                _cells(dtb, PCIE_PATH, "linux,pci-domain"),
                _cells(dtb, PCIE_PATH, "msi-map")[::2],
                _cells(dtb, PCIE_PATH, "iommu-map")[::2],
            )
        )

    # Then their machine-consumed PCI host contracts are identical and exact
    assert contracts[0] == contracts[1]
    assert contracts[0][:5] == (
        "pci-host-ecam-generic",
        EXPECTED_REG,
        EXPECTED_RANGES,
        (0, 0xFF),
        (4,),
    )


def test_maps_target_existing_its_and_smmu_when_fvp_dtbs_are_compiled(
    compiled_fvp_dtbs: tuple[Path, Path],
) -> None:
    # Given compiled hosts with RID translation maps
    # When map phandles and their targets are read from each DTB
    for dtb in compiled_fvp_dtbs:
        msi_map = _cells(dtb, PCIE_PATH, "msi-map")
        iommu_map = _cells(dtb, PCIE_PATH, "iommu-map")
        its_phandle = _cells(dtb, "/soc/interrupt-controller@20800000/msi-controller@20840000", "phandle")
        smmu_phandle = _cells(dtb, "/soc/iommu@1c0000000", "phandle")

        # Then all 16-bit RIDs map identically to the existing ITS and SMMU
        assert msi_map == (0, *its_phandle, *EXPECTED_MAP_SUFFIX)
        assert iommu_map == (0, *smmu_phandle, *EXPECTED_MAP_SUFFIX)
        assert _cells(dtb, "/soc/iommu@1c0000000", "reg") == (
            1,
            0xC0000000,
            0,
            0x08000000,
        )


def test_required_capabilities_when_fvp_dtbs_are_compiled(
    compiled_fvp_dtbs: tuple[Path, Path],
) -> None:
    # Given the two compiled PCIe4 hosts
    # When their boolean properties are queried
    for dtb in compiled_fvp_dtbs:
        properties = set(_run("fdtget", "-p", str(dtb), PCIE_PATH).split())

        # Then coherent DMA and ATS are enabled without legacy INTx plumbing
        assert {"dma-coherent", "ats-supported"} <= properties
        assert "interrupt-map" not in properties


def test_guest_contract_rejects_non_ap_visible_addresses(
    compiled_fvp_dtbs: tuple[Path, Path],
) -> None:
    # Given the FVP component-local and QBox-only PCI addresses
    forbidden_addresses = {0x43B50000, 0x4000000000, 0x4040000000}

    # When the compiled host address properties are inspected
    for dtb in compiled_fvp_dtbs:
        reg = _cells(dtb, PCIE_PATH, "reg")
        ranges = _cells(dtb, PCIE_PATH, "ranges")
        guest_addresses = {
            (reg[0] << 32) | reg[1],
            (ranges[3] << 32) | ranges[4],
            (ranges[10] << 32) | ranges[11],
        }

        # Then none of those non-guest address cells are present
        assert forbidden_addresses.isdisjoint(guest_addresses)
