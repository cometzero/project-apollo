import importlib.util
import json
import sys
from pathlib import Path


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


def write_behavior_evidence(tmp_path):
    stdout = tmp_path / "host-fixture.stdout"
    stdout.write_text(
        "\n".join(
            [
                "CASE corrupt-crc-default-a",
                "auto-ad-nexios: invalid misc, defaulting slot A",
                "ENV aanx_slot=A aanx_uki=EFI/Linux/auto-ad-nexios-a.efi",
                "SUMMARY PASS default-A fixture exercised parser and selector",
            ]
        )
        + "\n"
    )
    host = tmp_path / "task-07-host-fixture-result.json"
    host.write_text(
        json.dumps(
            {
                "status": "PASS",
                "c_fixture": {"stdout": str(stdout)},
                "bootcommand_fixture": {
                    "load_attempts": [
                        {"path": "EFI/Linux/auto-ad-nexios-a.efi"},
                        {"path": "EFI/Linux/auto-ad-nexios-b.efi"},
                    ],
                    "booted_path": "EFI/Linux/auto-ad-nexios-b.efi",
                },
            }
        )
        + "\n"
    )
    runtime = tmp_path / "task-12-negative-runtime-result.json"
    runtime.write_text(
        json.dumps(
            {
                "bad_rootro_runtime_status": {
                    "status": "PASS",
                    "result_json": "runtime/result.json",
                    "primary_uart": "runtime/terminal_ns_uart0.log",
                    "verdict": "dm-verity fail-closed",
                    "markers": {
                        "verity_corruption": True,
                        "verity_detected_corruption": True,
                        "mapper_mount_failed": True,
                        "kernel_panic_before_login": True,
                        "no_login_prompt": True,
                        "no_root_shell": True,
                        "no_verified_root_mount": True,
                    },
                }
            }
        )
        + "\n"
    )
    secure_boot = tmp_path / "secure-boot-parse.log"
    secure_boot.write_text(
        "ERROR: UEFI_SECURE_BOOT=1 requires UKI_SB_KEY and UKI_SB_CERT\n"
        "ERROR: Parsing halted due to errors, see error messages above\n"
        "[secure-boot-parse-exit] 1\n"
    )
    return host, runtime, secure_boot


def make_partitions(module):
    partitions = []
    offset = 0
    for number, name in enumerate(module.EXPECTED_ORDER, 1):
        size = module.parse_size(module.DEFAULT_EXPECTED[name])
        partitions.append(
            {
                "number": number,
                "start_sector": offset // module.SECTOR_SIZE,
                "end_sector": (offset + size) // module.SECTOR_SIZE - 1,
                "offset": offset,
                "size_bytes": size,
                "code": module.ESP_TYPE if name.startswith("boot_") else module.LINUX_TYPE,
                "name": name,
            }
        )
        offset += size
    return partitions


def make_misc_blob(module):
    misc_blob = bytearray(module.MISC_SIZE)
    misc_blob[:8] = module.MISC_MAGIC
    misc_blob[8:12] = (module.MISC_VERSION).to_bytes(4, "little")
    misc_blob[12:16] = (module.MISC_HEADER_SIZE).to_bytes(4, "little")
    misc_blob[16] = 0
    misc_blob[17] = 3
    misc_blob[18:20] = (0x0002).to_bytes(2, "little")
    crc = module.crc32_misc_header(misc_blob)
    misc_blob[module.MISC_CRC_OFFSET:module.MISC_CRC_OFFSET + 4] = crc.to_bytes(
        4, "little"
    )
    return misc_blob


def setup_negative_fixture(tmp_path, monkeypatch):
    module = load_module()
    wic = tmp_path / "fixture.wic"
    wic.write_bytes(b"fixture")
    partitions = make_partitions(module)
    misc_blob = make_misc_blob(module)

    def fake_read_exact(_path, offset, size):
        if offset == partitions[2]["offset"] and size == module.MISC_SIZE:
            return bytes(misc_blob)
        return b"\x00" * size

    def fake_copy_from_fat(_wic, _part, fat_path, out_path):
        if fat_path.endswith("auto-ad-nexios-a.efi"):
            content = b"MZ rootwait root=PARTLABEL=rootro_a ro console="
        elif fat_path.endswith("auto-ad-nexios-b.efi"):
            content = b"MZ rootwait root=PARTLABEL=rootro_b ro console="
        else:
            content = b"fixture"
        Path(out_path).write_bytes(content)

    monkeypatch.setattr(module, "parse_sgdisk", lambda _wic: partitions)
    monkeypatch.setattr(module, "check_filesystems", lambda _wic, _by_name: {})
    monkeypatch.setattr(module, "read_exact", fake_read_exact)
    monkeypatch.setattr(
        module,
        "inspect_verity",
        lambda _deploy_dir, _image_base: {"artifact": "verity", "env": "env"},
    )
    monkeypatch.setattr(
        module,
        "inspect_uboot_artifacts",
        lambda _deploy_dir: {"u_boot_bin": {"size": 1}, "initial_env": {"size": 1}},
    )
    helper = sys.modules["auto_ad_nexios_image_inspector_lib"]
    monkeypatch.setattr(helper, "copy_from_fat", fake_copy_from_fat)
    monkeypatch.setattr(module, "copy_from_fat", fake_copy_from_fat)
    (tmp_path / "auto-ad-nexios-a.efi").write_bytes(
        b"MZ rootwait root=PARTLABEL=rootro_a ro console="
    )
    (tmp_path / "auto-ad-nexios-b.efi").write_bytes(
        b"MZ rootwait root=PARTLABEL=rootro_b ro console="
    )
    return module, wic, tmp_path / "negative"


def test_negative_suite_records_behavior_backed_negative_results(tmp_path, monkeypatch):
    module, wic, work_dir = setup_negative_fixture(tmp_path, monkeypatch)
    host, runtime, secure_boot = write_behavior_evidence(tmp_path)

    assert module.main(
        [
            "--wic",
            str(wic),
            "--deploy-dir",
            str(tmp_path),
            "--negative-suite",
            "--work-dir",
            str(work_dir),
            "--host-fixture-evidence",
            str(host),
            "--negative-runtime-evidence",
            str(runtime),
            "--secure-boot-parse-log",
            str(secure_boot),
        ]
    ) == 0

    report = json.loads((work_dir / "negative-suite.json").read_text())
    assert report["result"] == "PASS"
    assert report["negative"]["corrupt_misc"]["status"] == "PASS"
    assert report["negative"]["corrupt_misc"]["stdout"] == str(tmp_path / "host-fixture.stdout")
    assert report["negative"]["missing_selected_uki"]["status"] == "PASS"
    assert report["negative"]["missing_selected_uki"]["booted_path"] == (
        "EFI/Linux/auto-ad-nexios-b.efi"
    )
    assert report["negative"]["bad_dm_verity_root"]["status"] == "PASS"
    assert report["negative"]["bad_dm_verity_root"]["markers"]["mapper_mount_failed"]
    assert report["negative"]["secure_boot_without_keys"]["status"] == "PASS"
    assert report["negative"]["secure_boot_without_keys"]["exit_code"] == 1
    assert not (
        work_dir
        / "esp-fixture"
        / "boot_a"
        / "EFI"
        / "Linux"
        / "auto-ad-nexios-a.efi"
    ).exists()
    assert (
        work_dir
        / "esp-fixture"
        / "boot_b"
        / "EFI"
        / "Linux"
        / "auto-ad-nexios-b.efi"
    ).exists()


def test_negative_suite_does_not_pass_without_external_behavior_evidence(
    tmp_path, monkeypatch
):
    module, wic, work_dir = setup_negative_fixture(tmp_path, monkeypatch)

    assert module.main(
        [
            "--wic",
            str(wic),
            "--deploy-dir",
            str(tmp_path),
            "--negative-suite",
            "--work-dir",
            str(work_dir),
            "--host-fixture-evidence",
            str(tmp_path / "missing-host.json"),
            "--negative-runtime-evidence",
            str(tmp_path / "missing-runtime.json"),
            "--secure-boot-parse-log",
            str(tmp_path / "missing-parse.log"),
        ]
    ) == 0

    report = json.loads((work_dir / "negative-suite.json").read_text())
    assert report["result"] == "EXTERNAL_EVIDENCE_REQUIRED"
    assert report["negative"]["corrupt_misc"]["status"] == "EXTERNAL_EVIDENCE_REQUIRED"
    assert report["negative"]["missing_selected_uki"]["status"] == (
        "EXTERNAL_EVIDENCE_REQUIRED"
    )
    assert report["negative"]["bad_dm_verity_root"]["status"] == "RUNTIME_REQUIRED"
    assert report["negative"]["secure_boot_without_keys"]["status"] == (
        "EXTERNAL_EVIDENCE_REQUIRED"
    )
