from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/test"))

from run_test_conf import ConfRequest, JsonObject, write_conf  # noqa: E402


def test_profile_target_overrides_functional_fvp_target(
    tmp_path: Path,
    monkeypatch,
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
