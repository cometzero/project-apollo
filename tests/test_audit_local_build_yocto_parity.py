from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/audit_local_build_yocto_parity.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "audit_local_build_yocto_parity",
        SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_vars(
    path: Path,
    variables: dict[str, dict[str, str]],
    schema_version: int | None = 1,
) -> None:
    recipes = {
        recipe: {"command": f"bitbake -e {recipe}", "variables": values}
        for recipe, values in variables.items()
    }
    payload = {
        "repo_root": str(ROOT),
        "build_dir": str(ROOT / "build"),
        "recipes": recipes,
    }
    if schema_version is not None:
        payload["schema_version"] = schema_version
    path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def test_audit_passes_when_sourced_defaults_match_capture(tmp_path: Path) -> None:
    module = load_module()
    vars_path = tmp_path / "vars.json"
    write_vars(
        vars_path,
        {
            "nexios-image": {
                "BOOTLOADER_LINUX_APPEND": "cpuidle.governor=menu maxcpus=4 mem=4064M",
                "MACHINE": "apollo-qvp",
                "PC_CPUS_COUNT_DEFAULT": "4",
                "RD_ASPEN_VARIANT": "cfg2",
            },
            "u-boot": {
                "MACHINE": "apollo-qvp",
                "RD_ASPEN_VARIANT": "cfg2",
                "UBOOT_MACHINE": "apollo_qvp_defconfig",
            },
            "linux-yocto-rt": {
                "KBUILD_DEFCONFIG": "apollo_qvp_defconfig",
                "KERNEL_DEVICETREE": "arm/apollo-qvp.dtb",
                "MACHINE": "apollo-qvp",
            },
            "optee-os": {"PLATFORM": "automotive_rd-rdaspen"},
        },
    )

    report = module.build_report(vars_path)
    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "pass"
    assert checks["boot_disk_bootargs_source"]["status"] == "pass"
    assert checks["optee_workdir_source"]["status"] == "pass"
    assert checks["machine"]["status"] == "pass"
    assert checks["pc_cpus_count"]["status"] == "pass"
    assert checks["rd_aspen_variant"]["status"] == "pass"
    assert checks["uboot_defconfig"]["status"] == "pass"
    assert checks["linux_dtb"]["status"] == "pass"
    assert checks["boot_disk_bootargs"]["local"].endswith(
        "cpuidle.governor=menu maxcpus=4 mem=4064M"
    )


def test_audit_catches_stale_env_override_against_capture(tmp_path: Path, monkeypatch) -> None:
    module = load_module()
    vars_path = tmp_path / "vars.json"
    write_vars(
        vars_path,
        {
            "nexios-image": {
                "BOOTLOADER_LINUX_APPEND": "cpuidle.governor=menu maxcpus=4 mem=4064M",
                "MACHINE": "apollo-qvp",
                "PC_CPUS_COUNT_DEFAULT": "4",
                "RD_ASPEN_VARIANT": "cfg2",
            },
            "u-boot": {"UBOOT_MACHINE": "apollo_qvp_defconfig"},
            "linux-yocto-rt": {
                "KBUILD_DEFCONFIG": "apollo_qvp_defconfig",
                "KERNEL_DEVICETREE": "arm/apollo-qvp.dtb",
            },
            "optee-os": {"PLATFORM": "automotive_rd-rdaspen"},
        },
    )
    monkeypatch.setenv("PC_CPUS_COUNT", "8")

    report = module.build_report(vars_path)
    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "pass"
    assert checks["pc_cpus_count"]["local"] == "4"


def test_audit_fails_when_captured_bootargs_have_stale_maxcpus(tmp_path: Path) -> None:
    module = load_module()
    vars_path = tmp_path / "vars.json"
    write_vars(
        vars_path,
        {
            "nexios-image": {
                "BOOTLOADER_LINUX_APPEND": "cpuidle.governor=menu maxcpus=4 mem=4064M",
                "MACHINE": "apollo-qvp",
                "PC_CPUS_COUNT_DEFAULT": "8",
                "RD_ASPEN_VARIANT": "cfg2",
            },
            "u-boot": {"UBOOT_MACHINE": "apollo_qvp_defconfig"},
            "linux-yocto-rt": {
                "KBUILD_DEFCONFIG": "apollo_qvp_defconfig",
                "KERNEL_DEVICETREE": "arm/apollo-qvp.dtb",
            },
            "optee-os": {"PLATFORM": "automotive_rd-rdaspen"},
        },
    )

    report = module.build_report(vars_path)
    checks = {check["id"]: check for check in report["checks"]}

    assert report["status"] == "fail"
    assert checks["bootloader_linux_append_maxcpus"]["status"] == "fail"
    assert checks["bootloader_linux_append_maxcpus"]["message"] == (
        "captured BOOTLOADER_LINUX_APPEND maxcpus=4 does not match "
        "captured PC_CPUS_COUNT_DEFAULT=8"
    )


def test_parse_capture_rejects_schema_version_mismatch(tmp_path: Path) -> None:
    module = load_module()
    vars_path = tmp_path / "vars.json"
    write_vars(vars_path, {"nexios-image": {"MACHINE": "apollo-fvp"}}, schema_version=2)

    try:
        module.parse_capture(vars_path)
    except module.AuditInputError as exc:
        assert "schema_version must be 1" in str(exc)
    else:
        raise AssertionError("parse_capture accepted schema_version != 1")


def test_parse_capture_rejects_missing_schema_version(tmp_path: Path) -> None:
    module = load_module()
    vars_path = tmp_path / "vars.json"
    write_vars(vars_path, {"nexios-image": {"MACHINE": "apollo-fvp"}}, schema_version=None)

    try:
        module.parse_capture(vars_path)
    except module.AuditInputError as exc:
        assert "schema_version must be 1" in str(exc)
    else:
        raise AssertionError("parse_capture accepted missing schema_version")


def test_out_of_scope_product_image_items_are_explicit(tmp_path: Path) -> None:
    module = load_module()
    vars_path = tmp_path / "vars.json"
    write_vars(vars_path, {"nexios-image": {"MACHINE": "apollo-fvp"}})

    report = module.build_report(vars_path)
    item_ids = {item["id"] for item in report["out_of_scope"]}

    assert {
        "full_product_rootfs",
        "wic_image_layout",
        "dm_verity_image",
        "product_image_packaging",
    }.issubset(item_ids)


def test_cli_writes_fail_report_for_missing_required_variable(tmp_path: Path) -> None:
    vars_path = tmp_path / "vars.json"
    output_path = tmp_path / "audit.json"
    write_vars(
        vars_path,
        {
            "nexios-image": {
                "PC_CPUS_COUNT_DEFAULT": "4",
                "RD_ASPEN_VARIANT": "cfg2",
            },
        },
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--vars",
            str(vars_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    report = json.loads(output_path.read_text(encoding="utf-8"))

    assert completed.returncode == 1
    assert report["status"] == "fail"
    assert any(
        check["id"] == "machine" and check["kind"] == "missing_yocto_var"
        for check in report["checks"]
    )
    assert "missing_yocto_var" in completed.stderr


def test_cli_writes_input_error_for_schema_version_mismatch(tmp_path: Path) -> None:
    vars_path = tmp_path / "vars.json"
    output_path = tmp_path / "audit.json"
    write_vars(vars_path, {"nexios-image": {"MACHINE": "apollo-fvp"}}, schema_version=2)

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--vars",
            str(vars_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    report = json.loads(output_path.read_text(encoding="utf-8"))

    assert completed.returncode == 1
    assert report["status"] == "fail"
    assert report["checks"] == [
        {
            "id": "input",
            "kind": "input_error",
            "status": "fail",
            "message": f"{vars_path}: schema_version must be 1",
        }
    ]
    assert "input_error" in completed.stderr


def test_cli_writes_input_error_for_missing_schema_version(tmp_path: Path) -> None:
    vars_path = tmp_path / "vars.json"
    output_path = tmp_path / "audit.json"
    write_vars(vars_path, {"nexios-image": {"MACHINE": "apollo-fvp"}}, schema_version=None)

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--vars",
            str(vars_path),
            "--output",
            str(output_path),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    report = json.loads(output_path.read_text(encoding="utf-8"))

    assert completed.returncode == 1
    assert report["status"] == "fail"
    assert report["checks"][0]["kind"] == "input_error"
    assert "schema_version must be 1" in report["checks"][0]["message"]
    assert "input_error" in completed.stderr
