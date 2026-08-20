from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pytest import MonkeyPatch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/test"))

from run_test_conf import ConfRequest, JsonObject, write_conf  # noqa: E402


PRODUCT_SUITES = (
    "test_00_fvp_boot",
    "test_00_rse_boot",
    "test_00_si_cl0_boot",
    "test_00_si_cl1_boot",
    "test_00_tfa_secure_partition_boot",
    "test_00_uboot_boot",
    "test_00_systemd_boot",
    "test_00_linux_boot",
    "test_00_safety_boot",
    "test_00_apollo_uki_boot",
    "test_21_si_cl0_pfdi",
    "test_22_si_cl0_smcf",
    "test_31_si_cl1_hipc",
    "test_40_tfa_cpu_topology",
    "test_41_tfa_ras",
    "test_60_linux_connectivity",
    "test_61_linux_dsu",
    "test_62_linux_cpu_topology",
    "test_63_linux_fvp_devices",
    "test_64_linux_pfdi",
    "test_65_linux_crypto",
    "test_70_power_scmi",
    "test_71_power_cpuidle",
    "test_72_power_cpufreq",
    "test_80_trusted_services",
)
BSP_SUITES = ("test_00_bsp_boot",)


def _bitbake_value(machine: str, image: str, variable: str) -> str:
    command = (
        "set +u; source layers/poky/oe-init-build-env build >/dev/null; "
        f"set -u; MACHINE={machine} bitbake-getvar -r {image} "
        f"--value {variable}"
    )
    result = subprocess.run(  # noqa: S602 - fixed matrix values only.
        ["bash", "-lc", command],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result.stdout.strip()


def test_profile_target_overrides_functional_fvp_target(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    # Given: a functional profile selecting the BSP serial target.
    monkeypatch.setenv("APOLLO_VALIDATION_TEST_SUITES", json.dumps(["test_x"]))
    monkeypatch.setenv("APOLLO_VALIDATION_TEST_TARGET", "HSOCBSPFVPTarget")
    request = ConfRequest(
        root=tmp_path,
        build_dir=Path("build"),
        machine="apollo-fvp",
        run_dir=Path("build/tests/run"),
        kind="functional",
    )
    manifest: JsonObject = {
        "machine": "apollo-fvp",
        "distro": "auto-ad-nexios",
    }

    # When: run-scoped OEQA configuration is generated.
    result = write_conf(request, manifest)

    # Then: the profile target takes precedence over the product target.
    assert result.conf_path is not None
    text = result.conf_path.read_text(encoding="utf-8")
    assert 'TEST_TARGET = "HSOCBSPFVPTarget"' in text
    assert "HSOCSingleSessionFVPTarget" not in text


@pytest.mark.parametrize("machine", ["apollo-fvp", "apollo-qvp"])
@pytest.mark.parametrize("image", ["nexios-image", "nexios-bsp-initramfs"])
def test_profile_assignments_include_selected_image_scope(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    machine: str,
    image: str,
) -> None:
    # Given: a focused profile with values distinct from every image default.
    monkeypatch.setenv("APOLLO_VALIDATION_TEST_SUITES", json.dumps(["test_x"]))
    monkeypatch.setenv("APOLLO_VALIDATION_TEST_TARGET", "ProfileFVPTarget")
    request = ConfRequest(
        root=tmp_path,
        build_dir=Path("build"),
        machine=machine,
        run_dir=Path("build/tests/run"),
        kind="functional",
        image=image,
    )
    manifest: JsonObject = {
        "machine": machine,
        "distro": "auto-ad-nexios",
        "image": image,
    }

    # When: the run-scoped configuration is generated.
    result = write_conf(request, manifest)

    # Then: both selected values carry the exact image recipe scope.
    assert result.conf_path is not None
    text = result.conf_path.read_text(encoding="utf-8")
    scope = f"{machine}:pn-{image}:auto-ad-nexios"
    assert f'TEST_SUITES:{scope} = "test_x"' in text
    assert f'TEST_TARGET:{scope} = "ProfileFVPTarget"' in text


def test_profile_assignment_rejects_malformed_image(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    # Given: an image value that could inject a second BitBake override.
    monkeypatch.setenv("APOLLO_VALIDATION_TEST_SUITES", json.dumps(["test_x"]))
    request = ConfRequest(
        root=tmp_path,
        build_dir=Path("build"),
        machine="apollo-fvp",
        run_dir=Path("build/tests/run"),
        kind="functional",
        image="nexios-image:malformed",
    )
    manifest: JsonObject = {
        "machine": "apollo-fvp",
        "distro": "auto-ad-nexios",
        "image": "nexios-image:malformed",
    }

    # When/Then: generation rejects the malformed recipe name.
    with pytest.raises(ValueError, match="invalid BitBake recipe name"):
        write_conf(request, manifest)


@pytest.mark.skipif(
    os.environ.get("APOLLO_RUN_BITBAKE_MATRIX_TESTS") != "1",
    reason="set APOLLO_RUN_BITBAKE_MATRIX_TESTS=1 for live BitBake parsing",
)
@pytest.mark.parametrize("machine", ["apollo-fvp", "apollo-qvp"])
@pytest.mark.parametrize(
    ("image", "expected_target", "expected_suites"),
    [
        ("nexios-image", "HSOCOEFVPTarget", PRODUCT_SUITES),
        ("nexios-bsp-initramfs", "HSOCBSPFVPTarget", BSP_SUITES),
    ],
)
def test_bitbake_image_validation_matrix(
    machine: str,
    image: str,
    expected_target: str,
    expected_suites: tuple[str, ...],
) -> None:
    # Given: the active layer stack and an explicit Apollo machine/image cell.
    # When: BitBake resolves the controller and ordered runtime suites.
    target = _bitbake_value(machine, image, "TEST_TARGET")
    suites = tuple(_bitbake_value(machine, image, "TEST_SUITES").split())

    # Then: the parsed values match the independent image contract fixture.
    assert target == expected_target
    assert suites == expected_suites
