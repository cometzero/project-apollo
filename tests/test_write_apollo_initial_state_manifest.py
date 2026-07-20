from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/inspect/write_apollo_initial_state_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "write_apollo_initial_state_manifest", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manifest_records_name_path_size_and_hash(tmp_path: Path) -> None:
    module = load_module()
    image = tmp_path / "rse-flash-image.img"
    image.write_bytes(b"initial-state")

    manifest = module.build_manifest([f"rse_flash={image}"])

    assert manifest["rse_flash"]["path"] == str(image.resolve())
    assert manifest["rse_flash"]["size"] == len(b"initial-state")
    assert manifest["rse_flash"]["sha256"] == module.sha256_file(image)
