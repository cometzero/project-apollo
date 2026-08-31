from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/build_gic720ae_pcie_its_profile.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(SCRIPT.stem, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_output_root_rejects_default_deploy() -> None:
    builder = load_builder()
    with pytest.raises(builder.ProfileError) as error:
        builder.ProfileLayout.create(
            ROOT / "build/tmp_baremetal/deploy/images/apollo-fvp/profile",
            ROOT,
        )
    assert error.value.reason == "active_default_path_forbidden"


@pytest.mark.parametrize("content", (None, b""))
def test_disk_must_exist_and_be_nonempty(
    tmp_path: Path, content: bytes | None,
) -> None:
    builder = load_builder()
    disk = tmp_path / "ahci.raw"
    if content is not None:
        disk.write_bytes(content)
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_scratch_disk(disk)
    assert error.value.reason in {"scratch_disk_missing", "scratch_disk_empty"}


def test_kernel_config_requires_irq_debugfs(tmp_path: Path) -> None:
    builder = load_builder()
    config = tmp_path / ".config"
    config.write_text("# CONFIG_GENERIC_IRQ_DEBUGFS is not set\n", encoding="utf-8")
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_kernel_config(config)
    assert error.value.reason == "irq_debugfs_missing"


@pytest.mark.parametrize("role", ("sigdata", "source", "output"))
def test_changed_hash_is_rejected(tmp_path: Path, role: str) -> None:
    builder = load_builder()
    path = tmp_path / role
    path.write_bytes(b"before")
    record = builder.hash_record(role, path)
    path.write_bytes(b"after")
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_hash_record(record)
    assert error.value.reason == "stale_hash"


def _compile_dtb(tmp_path: Path, *, include_pcie: bool = True, bad_reg: bool = False) -> Path:
    pcie = ""
    if include_pcie:
        reg = "<0x100 0x50000000 0 0x10000000>" if bad_reg else "<0x100 0x40000000 0 0x10000000>"
        pcie = "\n".join((
            "pcie@10040000000 {",
            'compatible = "pci-host-ecam-generic";',
            'device_type = "pci";',
            "#address-cells = <3>;",
            "#size-cells = <2>;",
            f"reg = {reg};",
            "ranges = <0x02000000 0 0x60000000 0 0x60000000 0 0x20000000",
            "0x43000000 0x101 0x60000000 0x101 0x60000000 0 0x20000000>;",
            "bus-range = <0 0xff>;",
            "linux,pci-domain = <4>;",
            "dma-coherent;",
            "ats-supported;",
            "msi-map = <0 1 0 0x10000>;",
            "iommu-map = <0 2 0 0x10000>;",
            "};",
        ))
    source = tmp_path / "test.dts"
    source.write_text("\n".join((
        "/dts-v1/;",
        "/ {",
        "#address-cells = <2>;",
        "#size-cells = <2>;",
        'interrupt-controller@20800000 { compatible = "arm,gic-v3";',
        "#address-cells = <2>; #size-cells = <2>;",
        "msi-controller@20840000 { phandle = <1>; reg = <0 0x20840000 0 0x20000>; };",
        "};",
        "iommu@1c0000000 { phandle = <2>; reg = <1 0xc0000000 0 0x08000000>; };",
        f"soc {{ #address-cells = <2>; #size-cells = <2>; {pcie} }};",
        "};",
        "",
    )), encoding="utf-8")
    output = tmp_path / "test.dtb"
    subprocess.run(["dtc", "-I", "dts", "-O", "dtb", "-o", output, source], check=True)
    return output


@pytest.mark.parametrize(
    ("include_pcie", "bad_reg", "reason"),
    ((False, False, "pcie_host_missing"), (True, True, "pcie_host_mismatch")),
)
def test_dtb_rejects_missing_or_mismatched_pcie_host(
    tmp_path: Path, include_pcie: bool, bad_reg: bool, reason: str,
) -> None:
    builder = load_builder()
    dtb = _compile_dtb(tmp_path, include_pcie=include_pcie, bad_reg=bad_reg)
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_dtb_contract(dtb)
    assert error.value.reason == reason


def test_uki_dtb_must_match_isolated_dtb(tmp_path: Path) -> None:
    builder = load_builder()
    expected = tmp_path / "expected.dtb"
    uki_a = tmp_path / "uki-a.dtb"
    uki_b = tmp_path / "uki-b.dtb"
    expected.write_bytes(b"expected")
    uki_a.write_bytes(b"different")
    uki_b.write_bytes(b"expected")
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_uki_dtbs(expected, [uki_a, uki_b])
    assert error.value.reason == "uki_dtb_mismatch"


def _valid_fvpconf(root: Path) -> dict[str, dict[str, str]]:
    disk = root / "ahci.raw"
    disk.write_bytes(b"disk")
    return {
        "parameters": {
            "pcie_group_0.pcie4.hierarchy_file_name": "<default>",
            "pcie_group_0.pcie4.pcie_rc.ahci0.endpoint.ats_supported": "true",
            "pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path": str(disk),
            "css.gic_distributor.ITS-count": "1",
        },
    }


@pytest.mark.parametrize(
    ("key", "value", "reason"),
    (
        ("pcie_group_0.pcie4.hierarchy_file_name", "custom.yml", "fvp_default_hierarchy_missing"),
        ("pcie_group_0.pcie4.pcie_rc.ahci0.endpoint.ats_supported", "false", "fvp_ats_disabled"),
        ("css.gic_distributor.ITS-count", "2", "fvp_its_count_mismatch"),
        ("pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path", "", "fvp_image_path_empty"),
    ),
)
def test_fvpconf_rejects_invalid_pcie_contract(
    tmp_path: Path, key: str, value: str, reason: str,
) -> None:
    builder = load_builder()
    config = _valid_fvpconf(tmp_path)
    parameters = config["parameters"]
    assert isinstance(parameters, dict)
    parameters[key] = value
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_fvp_config(config, tmp_path)
    assert error.value.reason == reason


def test_fvpconf_rejects_wrong_or_missing_image_path(tmp_path: Path) -> None:
    builder = load_builder()
    config = _valid_fvpconf(tmp_path)
    parameters = config["parameters"]
    assert isinstance(parameters, dict)
    parameters["pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path"] = str(
        tmp_path / "missing.raw"
    )
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_fvp_config(config, tmp_path)
    assert error.value.reason == "fvp_image_path_missing"


def test_fvpconf_rejects_reference_outside_profile(tmp_path: Path) -> None:
    builder = load_builder()
    root = tmp_path / "profile"
    root.mkdir()
    config = _valid_fvpconf(root)
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"outside")
    parameters = config["parameters"]
    assert isinstance(parameters, dict)
    parameters["ros.flash_loader.fname"] = str(outside)
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_fvp_config(config, root)
    assert error.value.reason == "profile_path_escape"


def test_schema_accepts_minimal_failure_receipt(tmp_path: Path) -> None:
    builder = load_builder()
    schema = json.loads((ROOT / "tests/schemas/gic720ae-pcie-its-profile.schema.json").read_text())
    builder.validate_receipt(builder.failure_receipt("test_failure", tmp_path), schema)


def test_environment_log_excludes_unrelated_host_values() -> None:
    builder = load_builder()
    output = "\n".join((
        'APOLLO_KERNEL_CONFIG_FRAGMENT="gic720ae-pcie-its.cfg"',
        'TMPDIR="/isolated/tmp"',
        'UNRELATED_SECRET="must-not-be-recorded"',
    ))
    safe = builder.safe_log_output("profile-kernel-environment.log", output)
    assert "APOLLO_KERNEL_CONFIG_FRAGMENT" in safe
    assert "TMPDIR" in safe
    assert "UNRELATED_SECRET" not in safe
    assert "must-not-be-recorded" not in safe


def test_output_capacity_requires_48_gib() -> None:
    builder = load_builder()
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_output_capacity((48 * 1024**3) - 1)
    assert error.value.reason == "insufficient_output_capacity"


def test_externalsrc_fragment_uses_owner_path_not_src_uri() -> None:
    metadata = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/"
        "linux-yocto-apollo-common.inc"
    ).read_text(encoding="utf-8")
    assert "SRC_URI:append" not in metadata
    assert "APOLLO_KERNEL_CONFIG_FRAGMENT_PATH" in metadata
    assert "${APOLLO_KERNEL_CONFIG_FRAGMENT_PATH}" in metadata


@pytest.mark.parametrize("missing", ("generated", "extracted"))
def test_fip_hw_config_must_exist(tmp_path: Path, missing: str) -> None:
    builder = load_builder()
    generated = tmp_path / "generated.dtb"
    extracted = tmp_path / "extracted.dtb"
    if missing != "generated":
        generated.write_bytes(b"same")
    if missing != "extracted":
        extracted.write_bytes(b"same")
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_fip_hw_config(extracted, generated)
    assert error.value.reason == "fip_hw_config_missing"


def test_fip_hw_config_must_match_generated(tmp_path: Path) -> None:
    builder = load_builder()
    generated = tmp_path / "generated.dtb"
    extracted = tmp_path / "extracted.dtb"
    generated.write_bytes(b"generated")
    extracted.write_bytes(b"different")
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_fip_hw_config(extracted, generated)
    assert error.value.reason == "fip_hw_config_mismatch"


def test_absent_mode_rejects_unexpected_uki_dtb() -> None:
    builder = load_builder()
    sections = {"a": [".linux", ".dtb"], "b": [".linux"]}
    with pytest.raises(builder.ProfileError) as error:
        builder.validate_uki_sections(sections)
    assert error.value.reason == "unexpected_uki_dtb"


def test_linux_raw_dtb_cannot_claim_runtime_consumption(tmp_path: Path) -> None:
    builder = load_builder()
    dtb = tmp_path / "apollo-fvp.dtb"
    dtb.write_bytes(b"reference")
    with pytest.raises(builder.ProfileError) as error:
        builder.linux_dtb_reference(dtb, "consumed")
    assert error.value.reason == "false_linux_dtb_consumption_claim"
