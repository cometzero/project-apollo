from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/test"))

from run_test_manifest import ManifestInputs, selected_artifacts  # noqa: E402


def test_manifest_selects_bsp_artifacts() -> None:
    # Given: an Apollo FVP BSP manifest request.
    inputs = ManifestInputs(
        root=ROOT,
        build_dir=Path("build"),
        machine="apollo-fvp",
        image="nexios-bsp-initramfs",
    )

    # When: deploy inputs are resolved.
    testdata, fvpconf = selected_artifacts(inputs, "${TOPDIR}/tmp_baremetal")

    # Then: both paths use the requested BSP image basename.
    assert testdata.name == "nexios-bsp-initramfs-apollo-fvp.testdata.json"
    assert fvpconf.name == "nexios-bsp-initramfs-apollo-fvp.fvpconf"
