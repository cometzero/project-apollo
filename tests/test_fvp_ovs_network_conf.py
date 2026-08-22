from __future__ import annotations

import configparser
import os
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
RECIPE = "arm-auto-solutions-network-conf"
NETWORK_FILE = Path("etc/systemd/network/10-ovsbr0.network")
PROJECT_NETWORK_FILE = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core"
    / "arm-auto-solutions-network-conf/files/10-ovsbr0.network"
)
UPSTREAM_NETWORK_FILE = (
    ROOT
    / "sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core"
    / "arm-auto-solutions-network-conf/files/common/network/10-ovsbr0.network"
)


def _bitbake_value(machine: str, variable: str) -> str:
    command = (
        "set +u; source layers/poky/oe-init-build-env build >/dev/null; "
        f"set -u; MACHINE={machine} bitbake-getvar -q -r {RECIPE} "
        f"--value {variable}"
    )
    result = subprocess.run(  # noqa: S602 - fixed machine and recipe values.
        ["bash", "-lc", command],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    values = [
        line
        for line in result.stdout.splitlines()
        if line and not line.startswith("NOTE:")
    ]
    assert values
    return values[-1]


def _network_config(path: Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser(interpolation=None, strict=True)
    with path.open(encoding="utf-8") as network_file:
        config.read_file(network_file)
    return config


@pytest.mark.skipif(
    os.environ.get("RUN_YOCTO_MATRIX") != "1",
    reason="requires the active Yocto install artifact",
)
def test_apollo_fvp_installed_ovsbr0_configures_without_carrier() -> None:
    # Given: the active Apollo FVP network configuration recipe install tree.
    install_root = Path(_bitbake_value("apollo-fvp", "D"))
    installed = install_root / NETWORK_FILE
    assert installed.is_file()

    # When: the installed networkd file is parsed strictly.
    config = _network_config(installed)

    # Then: DHCP remains enabled and carrierless configuration is explicit.
    assert config.sections() == ["Match", "Network"]
    assert config.get("Match", "Name") == "ovsbr0"
    assert config.get("Network", "DHCP") == "ipv4"
    assert config.get("Network", "ConfigureWithoutCarrier") == "yes"
    assert not config.has_option("Network", "IgnoreCarrierLoss")


def test_project_ovsbr0_override_has_one_exact_network_policy() -> None:
    # Given: the project-owned Apollo FVP networkd replacement.
    assert PROJECT_NETWORK_FILE.is_file()

    # When: it is parsed without duplicate sections or keys.
    config = _network_config(PROJECT_NETWORK_FILE)

    # Then: only DHCP and carrierless configuration are added.
    assert config.sections() == ["Match", "Network"]
    assert dict(config.items("Match")) == {"name": "ovsbr0"}
    assert dict(config.items("Network")) == {
        "dhcp": "ipv4",
        "configurewithoutcarrier": "yes",
    }


@pytest.mark.skipif(
    os.environ.get("RUN_YOCTO_MATRIX") != "1",
    reason="requires active Yocto recipe environments",
)
def test_carrierless_override_is_scoped_to_apollo_fvp_baremetal() -> None:
    # Given: final FVP and QVP environments for the shared upstream recipe.
    fvp_arch = _bitbake_value("apollo-fvp", "PACKAGE_ARCH")
    fvp_uri = _bitbake_value("apollo-fvp", "SRC_URI")
    qvp_arch = _bitbake_value("apollo-qvp", "PACKAGE_ARCH")
    qvp_uri = _bitbake_value("apollo-qvp", "SRC_URI")

    # When/Then: only FVP is machine-arch and fetches the project file.
    assert fvp_arch == "apollo_fvp"
    assert "file://10-ovsbr0.network" in fvp_uri.split()
    assert qvp_arch == "all"
    assert "file://10-ovsbr0.network" not in qvp_uri.split()


@pytest.mark.skipif(
    os.environ.get("RUN_YOCTO_MATRIX") != "1",
    reason="requires the active Yocto install artifact",
)
def test_apollo_qvp_selected_source_keeps_upstream_carrier_policy() -> None:
    # Given: QVP final SRC_URI excludes the FVP project replacement.
    qvp_uri = _bitbake_value("apollo-qvp", "SRC_URI")
    assert "file://10-ovsbr0.network" not in qvp_uri.split()
    assert UPSTREAM_NETWORK_FILE.is_file()

    # When: the selected upstream QVP file is parsed strictly.
    config = _network_config(UPSTREAM_NETWORK_FILE)

    # Then: upstream DHCP remains and FVP carrier policy does not leak.
    assert config.get("Network", "DHCP") == "ipv4"
    assert not config.has_option("Network", "ConfigureWithoutCarrier")
