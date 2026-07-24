import json
import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "test"
    / "inspect_auto_ad_nexios_image.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("aanx_inspector", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_expect_partitions_requires_name_size_pairs():
    module = load_module()

    with pytest.raises(module.InspectError):
        module.parse_expect_partitions("boot")


def test_parse_expect_partitions_accepts_contract():
    module = load_module()

    expected = module.parse_expect_partitions(
        "boot=256M,misc=4M,"
        "rootro_a=8192M,rootro_b=8192M,rootrw=512M,data=4096M"
    )

    assert list(expected) == module.EXPECTED_ORDER
    assert module.parse_size(expected["rootro_a"]) == 8192 * 1024 * 1024


@pytest.mark.parametrize("machine", ["apollo-fvp", "apollo-qvp"])
def test_esp_required_files_accept_direct_uki_layout_without_boot_conf(
    tmp_path, monkeypatch, machine
):
    module = load_module()
    helper = sys.modules["auto_ad_nexios_image_inspector_lib"]
    wic = tmp_path / "fixture.wic"
    wic.write_bytes(b"fixture")
    json_out = tmp_path / "summary.json"
    partitions = []
    for number, name in enumerate(module.EXPECTED_ORDER, 1):
        start = number * 100000
        size = module.parse_size(module.DEFAULT_EXPECTED[name])
        partitions.append(
            {
                "number": number,
                "start_sector": start,
                "end_sector": start + (size // module.SECTOR_SIZE) - 1,
                "offset": start * module.SECTOR_SIZE,
                "size_bytes": size,
                "code": module.ESP_TYPE if name == "boot" else module.LINUX_TYPE,
                "name": name,
            }
        )
    copied = []

    def fat_bytes(fat_path):
        if fat_path.endswith("a-slot/metadata"):
            return b"slot=A\n"
        if fat_path.endswith("b-slot/metadata"):
            return b"slot=B\n"
        if fat_path.endswith("auto-ad-nexios-a.efi"):
            return b"MZ rootwait root=PARTLABEL=rootro_a ro console=ttyAMA0,115200"
        if fat_path.endswith("auto-ad-nexios-b.efi"):
            return b"MZ rootwait root=PARTLABEL=rootro_b ro console=ttyAMA0,115200"
        return f"copied:{fat_path}".encode()

    def fake_copy_from_fat(_wic, part, fat_path, out_path):
        copied.append((part["name"], fat_path))
        Path(out_path).write_bytes(fat_bytes(fat_path))

    (tmp_path / "auto-ad-nexios-a.efi").write_bytes(
        fat_bytes("::/EFI/Linux/a-slot/auto-ad-nexios-a.efi")
    )
    (tmp_path / "auto-ad-nexios-b.efi").write_bytes(
        fat_bytes("::/EFI/Linux/b-slot/auto-ad-nexios-b.efi")
    )
    (tmp_path / f"u-boot-{machine}-test.bin").write_bytes(b"u-boot")
    (tmp_path / f"u-boot-initial-env-{machine}-test").write_bytes(b"env")
    monkeypatch.setattr(module, "parse_sgdisk", lambda _wic: partitions)
    monkeypatch.setattr(module, "check_filesystems", lambda _wic, _by_name: {})
    monkeypatch.setattr(
        module,
        "inspect_misc",
        lambda _wic, _misc_part, _slot: {"slot": "A"},
    )
    monkeypatch.setattr(
        module,
        "inspect_verity",
        lambda _deploy_dir, _image_base: {"artifact": "verity", "env": "env"},
    )
    monkeypatch.setattr(helper, "copy_from_fat", fake_copy_from_fat)

    assert module.main(
        ["--wic", str(wic), "--deploy-dir", str(tmp_path), "--json", str(json_out)]
    ) == 0
    summary = json.loads(json_out.read_text())

    assert summary["result"] == "PASS"
    assert "/EFI/BOOT/bootaa64.efi" in summary["esp"]["files"]
    assert (
        "/EFI/Linux/a-slot/auto-ad-nexios-a.efi"
        in summary["esp"]["slots"]["a-slot"]["files"]
    )
    assert (
        "/EFI/Linux/b-slot/auto-ad-nexios-b.efi"
        in summary["esp"]["slots"]["b-slot"]["files"]
    )
    assert "/loader/entries/boot.conf" not in summary["esp"]["files"]
    assert "/Image.unsigned" not in summary["esp"]["files"]
    assert summary["esp"]["slots"]["a-slot"]["metadata_slot"] == "A"
    assert summary["esp"]["slots"]["b-slot"]["metadata_slot"] == "B"
    assert summary["esp"]["slots"]["a-slot"]["uki_cmdline_root"] == "rootro_a"
    assert summary["esp"]["slots"]["b-slot"]["uki_cmdline_root"] == "rootro_b"
    assert summary["u_boot"]["u_boot_bin"]["size"] == 6
    assert all(
        "loader/entries/boot.conf" not in path
        for slot in ("a-slot", "b-slot")
        for path in summary["esp"]["slots"][slot]["files"]
    )
    assert (
        "boot",
        "::/EFI/Linux/b-slot/auto-ad-nexios-b.efi",
    ) in copied


def test_esp_inspection_rejects_missing_slot_uki(tmp_path, monkeypatch):
    module = load_module()
    helper = sys.modules["auto_ad_nexios_image_inspector_lib"]
    wic = tmp_path / "fixture.wic"
    wic.write_bytes(b"fixture")
    by_name = {"boot": {"name": "boot", "offset": 0}}

    def fake_copy_from_fat(_wic, _part, fat_path, out_path):
        if fat_path.endswith("a-slot/metadata"):
            Path(out_path).write_bytes(b"slot=A\n")
            return
        if fat_path.endswith("b-slot/metadata"):
            Path(out_path).write_bytes(b"slot=B\n")
            return
        if fat_path.endswith("auto-ad-nexios-b.efi"):
            raise module.InspectError(f"missing FAT file {fat_path}: not found")
        content = b"rootwait root=PARTLABEL=rootro_a ro console="
        Path(out_path).write_bytes(content)

    (tmp_path / "auto-ad-nexios-a.efi").write_bytes(
        b"rootwait root=PARTLABEL=rootro_a ro console="
    )
    (tmp_path / "auto-ad-nexios-b.efi").write_bytes(
        b"rootwait root=PARTLABEL=rootro_b ro console="
    )
    monkeypatch.setattr(helper, "copy_from_fat", fake_copy_from_fat)

    with pytest.raises(module.InspectError, match="auto-ad-nexios-b.efi"):
        module.inspect_esp_slots(wic, by_name, "0", tmp_path)


def test_misc_default_slot_b_negative_probe_fails_on_default_a(tmp_path):
    module = load_module()
    blob = bytearray(module.MISC_SIZE)
    blob[:8] = module.MISC_MAGIC
    blob[8:12] = (module.MISC_VERSION).to_bytes(4, "little")
    blob[12:16] = (module.MISC_HEADER_SIZE).to_bytes(4, "little")
    blob[16] = 0
    blob[17] = 3
    blob[18:20] = (0x0002).to_bytes(2, "little")
    blob[20:24] = (0).to_bytes(4, "little")
    crc = module.crc32_misc_header(blob)
    blob[module.MISC_CRC_OFFSET:module.MISC_CRC_OFFSET + 4] = (
        crc.to_bytes(4, "little")
    )
    wic = tmp_path / "fixture.wic"
    wic.write_bytes(bytes(blob))
    part = {"offset": 0}

    with pytest.raises(module.InspectError, match="expected B, got A"):
        module.inspect_misc(wic, part, "B")


def test_check_partition_contract_rejects_two_partition_baseline():
    module = load_module()
    partitions = [
        {
            "number": 1,
            "start_sector": 2048,
            "end_sector": 526335,
            "offset": 2048 * module.SECTOR_SIZE,
            "size_bytes": 256 * 1024 * 1024,
            "code": module.ESP_TYPE,
            "name": "ESP",
        },
        {
            "number": 2,
            "start_sector": 526336,
            "end_sector": 3010967,
            "offset": 526336 * module.SECTOR_SIZE,
            "size_bytes": 1272070144,
            "code": module.LINUX_TYPE,
            "name": "rootfs",
        },
    ]

    with pytest.raises(module.InspectError, match="partition order/name mismatch"):
        module.check_partition_contract(partitions, module.DEFAULT_EXPECTED)


def test_check_filesystems_allows_unlabeled_rootro_partitions(monkeypatch):
    module = load_module()
    artifacts = sys.modules["auto_ad_nexios_image_inspector_artifacts"]
    by_name = {name: {"name": name} for name in module.EXPECTED_ORDER}

    def fake_blkid_probe(_wic, part):
        name = part["name"]
        if name == "boot":
            return {"probed": True, "TYPE": "vfat", "LABEL_FATBOOT": name}
        if name in ("rootro_a", "rootro_b"):
            return {"probed": True, "TYPE": "ext4"}
        return {"probed": True, "TYPE": "ext4", "LABEL": name}

    monkeypatch.setattr(artifacts, "blkid_probe", fake_blkid_probe)

    result = module.check_filesystems("fixture.wic", by_name)

    assert result["rootro_a"]["TYPE"] == "ext4"
    assert "LABEL" not in result["rootro_a"]


def test_check_filesystems_still_requires_mutable_partition_labels(monkeypatch):
    module = load_module()
    artifacts = sys.modules["auto_ad_nexios_image_inspector_artifacts"]
    by_name = {name: {"name": name} for name in module.EXPECTED_ORDER}

    def fake_blkid_probe(_wic, part):
        name = part["name"]
        if name == "boot":
            return {"probed": True, "TYPE": "vfat", "LABEL_FATBOOT": name}
        if name in ("rootro_a", "rootro_b"):
            return {"probed": True, "TYPE": "ext4"}
        if name == "data":
            return {"probed": True, "TYPE": "ext4"}
        return {"probed": True, "TYPE": "ext4", "LABEL": name}

    monkeypatch.setattr(artifacts, "blkid_probe", fake_blkid_probe)

    with pytest.raises(module.InspectError, match="partition data label mismatch"):
        module.check_filesystems("fixture.wic", by_name)
