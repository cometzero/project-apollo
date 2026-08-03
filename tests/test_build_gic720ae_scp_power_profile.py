from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/test/build_gic720ae_scp_power_profile.py"
SPEC = importlib.util.spec_from_file_location("scp_power_profile", BUILDER)
assert SPEC is not None and SPEC.loader is not None
SCP_POWER_PROFILE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCP_POWER_PROFILE
SPEC.loader.exec_module(SCP_POWER_PROFILE)


def make_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    output_root = tmp_path / "gic720ae-scp-power-test"
    binary = output_root / "deploy/firmware/si0_ramfw.bin"
    elf = output_root / "work/scp-firmware/bin/apollo-qvp-si0-bl2.elf"
    binary.parent.mkdir(parents=True)
    elf.parent.mkdir(parents=True)
    binary.write_bytes(b"isolated-si0-bin")
    elf.write_bytes(b"isolated-si0-elf")
    default_configure = tmp_path / "default-configure.txt"
    default_configure.write_text("SCP_ENABLE_GIC_POWER_TEST:BOOL=0\n", encoding="utf-8")
    return output_root, binary, default_configure


def invoke(tmp_path: Path, *extra: str) -> tuple[subprocess.CompletedProcess[str], Path]:
    profile = tmp_path / "profile.json"
    result = subprocess.run(
        [
            sys.executable, str(BUILDER), "--check-only",
            "--source", "hsoc-stack/components/system_mgmt/scp-firmware",
            "--require-local-build-source-closure",
            "--require-recipe-sysroot-taskhash", "--platform", "apollo-qvp",
            "--profile-output", str(profile), *extra,
        ],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    return result, profile


def make_taskhash_shape(tmp_path: Path) -> tuple[dict[str, str], Path]:
    # Given: a task run marker, its exact sigdata, and its exact sstate tuple.
    taskhash = "a" * 64
    stamp = (
        tmp_path / "tmp_baremetal/stamps/apollo_qvp-poky-linux/scp-firmware"
        / "2.16.0+git"
    )
    stamp.parent.mkdir(parents=True)
    Path(f"{stamp}.do_prepare_recipe_sysroot.{taskhash}").write_text("", encoding="utf-8")
    Path(f"{stamp}.do_prepare_recipe_sysroot.sigdata.{taskhash}").write_text("sigdata", encoding="utf-8")
    sstate = tmp_path / "sstate-cache/aa/bb"
    sstate.mkdir(parents=True)
    tuple_path = sstate / (
        "sstate:scp-firmware:apollo_qvp-poky-linux:2.16.0+git:r0:"
        f"apollo_qvp:14:{taskhash}_prepare_recipe_sysroot.tar.zst.siginfo"
    )
    tuple_path.write_text("sstate", encoding="utf-8")
    return {
        "STAMP": str(stamp), "SSTATE_DIR": str(tmp_path / "sstate-cache"),
        "PN": "scp-firmware", "PV": "2.16.0+git", "PR": "r0",
        "SSTATE_PKGARCH": "apollo_qvp", "SSTATE_VERSION": "14",
    }, tuple_path


def test_taskhash_selection_uses_active_apollo_qvp_marker_and_tuple(tmp_path: Path) -> None:
    # Given: the real active-QVP filesystem naming shape.
    values, tuple_path = make_taskhash_shape(tmp_path)

    # When: provenance selects the taskhash from the task run marker.
    provenance = SCP_POWER_PROFILE.select_task_provenance(values)

    # Then: it binds only the corresponding sigdata and sstate tuple.
    assert provenance["taskhash"] == "a" * 64
    assert provenance["siginfo"].startswith(
        f"{values['STAMP']}.do_prepare_recipe_sysroot.sigdata.{'a' * 64}:"
    )
    assert provenance["sstate"].startswith(f"{tuple_path}:")


def test_taskhash_selection_rejects_stale_or_fvp_tuple(tmp_path: Path) -> None:
    # Given: a valid QVP marker but only stale/FVP sstate tuples.
    values, tuple_path = make_taskhash_shape(tmp_path)
    tuple_path.unlink()
    stale = "b" * 64
    Path(f"{values['STAMP']}.do_prepare_recipe_sysroot.sigdata.{stale}").write_text("stale", encoding="utf-8")
    stale_tuple = Path(values["SSTATE_DIR"]) / "cc/dd" / (
        "sstate:scp-firmware:apollo_fvp-poky-linux:2.16.0+git:r0:"
        f"apollo_fvp:14:{stale}_prepare_recipe_sysroot.tar.zst.siginfo"
    )
    stale_tuple.parent.mkdir(parents=True)
    stale_tuple.write_text("stale", encoding="utf-8")

    # When / Then: neither mismatched taskhash nor FVP machine is accepted.
    with pytest.raises(ValueError, match="missing_recipe_sysroot_taskhash"):
        SCP_POWER_PROFILE.select_task_provenance(values)


def test_taskhash_selection_rejects_multiple_matching_siginfo_tuples(tmp_path: Path) -> None:
    # Given: two sstate siginfo files for the same otherwise exact tuple.
    values, tuple_path = make_taskhash_shape(tmp_path)
    duplicate = tuple_path.parents[2] / "cc/dd" / tuple_path.name
    duplicate.parent.mkdir(parents=True)
    duplicate.write_text("duplicate", encoding="utf-8")

    # When / Then: provenance fails closed instead of choosing by timestamp.
    with pytest.raises(ValueError, match="ambiguous_recipe_sysroot_taskhash"):
        SCP_POWER_PROFILE.select_task_provenance(values)


def test_profile_contract_emits_literal_isolated_command_and_hashes(tmp_path: Path) -> None:
    # Given: real isolated SCP output files and a default configure record.
    output_root, binary, default_configure = make_inputs(tmp_path)
    elf = output_root / "work/scp-firmware/bin/apollo-qvp-si0-bl2.elf"

    # When: the producer validates the inputs without launching a build.
    result, profile = invoke(
        tmp_path, "--output-root", str(output_root),
        "--default-configure-record", str(default_configure),
    )

    # Then: its structured receipt binds the literal command and file hashes.
    assert result.returncode == 0, result.stderr
    payload = json.loads(profile.read_text(encoding="utf-8"))
    assert payload["verdict"] == "PASS"
    assert payload["command"] == [
        "LOCAL_BUILD_DIR=" + str(output_root),
        "SCP_ENABLE_GIC_POWER_TEST=1", "./local_build.sh", "scp-firmware", "clean-build",
    ]
    assert payload["outputs"] == [
        {"role": "si0_ramfw.bin", "path": str(binary.resolve()), "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()},
        {"role": "apollo-qvp-si0-bl2.elf", "path": str(elf.resolve()), "sha256": hashlib.sha256(elf.read_bytes()).hexdigest()},
    ]
    assert payload["default_exclusion"] == {
        "test-gic-power": 0, "test gic_power": 0, "FWK_MODULE_IDX_TEST_GIC_POWER": 0,
    }
    assert payload["provenance"]["required_task"] == "scp-firmware:do_prepare_recipe_sysroot"
    assert set(payload["provenance"]["owners"]) == {
        ".", "hsoc-stack/components/system_mgmt/scp-firmware",
        "hsoc-stack/yocto/meta-hsoc-auto-solutions", "hsoc-stack/yocto/meta-hsoc-bsp",
        "layers/meta-arm", "layers/poky",
    }
    assert payload["provenance"]["active_bblayer_heads"]


def test_profile_contract_uses_the_default_build_contract_when_not_overridden(tmp_path: Path) -> None:
    output_root, _, _ = make_inputs(tmp_path)

    result, profile = invoke(tmp_path, "--output-root", str(output_root))

    assert result.returncode == 0, result.stderr
    payload = json.loads(profile.read_text(encoding="utf-8"))
    assert payload["default_exclusion"] == {
        "test-gic-power": 0, "test gic_power": 0, "FWK_MODULE_IDX_TEST_GIC_POWER": 0,
    }
    assert payload["provenance"]["default_configure_record"].endswith(
        "scripts/build/modules/build_scp.sh"
    )


def test_profile_contract_rejects_default_test_contamination(tmp_path: Path) -> None:
    # Given: an isolated output family but a default configure that contains test wiring.
    output_root, _, default_configure = make_inputs(tmp_path)
    default_configure.write_text("test-gic-power\n", encoding="utf-8")

    # When: the default exclusion audit runs.
    result, profile = invoke(
        tmp_path, "--output-root", str(output_root),
        "--default-configure-record", str(default_configure),
    )

    # Then: it fails closed instead of accepting production contamination.
    assert result.returncode != 0
    assert json.loads(profile.read_text(encoding="utf-8"))["reason"] == "default_configuration_contaminated"


def test_profile_contract_rejects_nonisolated_output_root(tmp_path: Path) -> None:
    # Given: a path that is not the dedicated SCP power profile root.
    output_root, _, default_configure = make_inputs(tmp_path)

    # When: a caller tries to relabel that output as a normal local build directory.
    result, profile = invoke(
        tmp_path, "--output-root", str(output_root.parent / "local-apollo-qvp"),
        "--default-configure-record", str(default_configure),
    )

    # Then: the producer records the failed isolation contract.
    assert result.returncode != 0
    assert json.loads(profile.read_text(encoding="utf-8"))["reason"] == "nonisolated_output_root"
