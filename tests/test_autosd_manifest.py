"""Validate the full-system AutoSD manifest contract."""

import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/run"))
from autosd_manifest import autosd_manifest


@pytest.mark.parametrize("changes", [{"mode": "invalid"}, {"rootfs": "relative.raw"},
                                     {"initrd": None}, {"bootargs": ""}])
def test_autosd_manifest_rejects_invalid_fields(tmp_path, changes):
    manifest = {"mode": "regular", "rootfs": "/disk.raw", "initrd": "/initrd",
                "bootargs": "console=ttyAMA0"}
    manifest.update(changes)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        autosd_manifest(path)
