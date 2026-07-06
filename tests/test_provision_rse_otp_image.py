from __future__ import annotations

import importlib.util
from pathlib import Path
import types


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/setup/provision_rse_otp_image.py"


def load_provision_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("provision_rse_otp_image", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_find_site_packages_uses_machine_agnostic_workdirs(tmp_path: Path) -> None:
    module = load_provision_module()
    qvp_site = (
        tmp_path
        / "build/tmp_baremetal/work/apollo_qvp-poky-linux/trusted-firmware-m"
        / "2.2.2+git/recipe-sysroot-native/usr/lib/python3.13/site-packages"
    )
    component_site = (
        tmp_path
        / "build/tmp_baremetal/sysroots-components/x86_64"
        / "trusted-firmware-m-scripts-native/usr/lib/python3.13/site-packages"
    )
    qvp_site.mkdir(parents=True)
    component_site.mkdir(parents=True)

    result = module.find_site_packages(tmp_path, tmp_path / "tfm-build")

    assert qvp_site in result
    assert component_site in result
