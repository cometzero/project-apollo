from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import ModuleType

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/validate_apollo_fvp_pcie_limit.py"
FIXTURE = ROOT / "tests/fixtures/gic720ae/pcie-its/fvp-limit"
SCHEMA = ROOT / "tests/schemas/apollo-fvp-pcie-limit.schema.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def invoke(tmp_path: Path) -> tuple[int, dict[str, str | bool | dict[str, str]]]:
    output = tmp_path / "limit.json"
    result = subprocess.run([sys.executable, str(SCRIPT), "--output", str(output)], cwd=ROOT, text=True, capture_output=True, check=False)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return result.returncode, payload


def fixture_modules() -> tuple[ModuleType, ModuleType]:
    manifest = load_module("apollo_fvp_pcie_limit_manifest", ROOT / "scripts/test/apollo_fvp_pcie_limit_manifest.py")
    validator = load_module("validate_apollo_fvp_pcie_limit", SCRIPT)
    return manifest, validator


def test_offline_fixture_reproduces_only_the_unsupported_boundary(tmp_path: Path) -> None:
    # Given: the checked-in fixture includes a manifest and original identities.
    identity = json.loads((FIXTURE / "source-identity.json").read_text(encoding="utf-8"))
    manifest = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))
    assert identity["binary"]["sha256"] == "28b63033b06f083b74fcf954ac05cd0f2bd8fcc6babac0bdc5cecd0159f96c05"
    assert set(entry["path"] for entry in manifest["inputs"].values()) == {path.name for path in FIXTURE.iterdir() if path.is_file() and path.name != "manifest.json"}
    assert "does not assert" in (FIXTURE / "NOTICE").read_text(encoding="utf-8")
    assert not any("/srv" in path.read_text(encoding="utf-8") for path in FIXTURE.iterdir() if path.is_file())

    # When: the validator consumes only the repository fixture.
    returncode, payload = invoke(tmp_path)

    # Then: it records the exact limitation without physical ITS or parity claims.
    assert returncode == 0
    assert payload["reference_gate"] == "PASS"
    assert payload["fvp_qualification"] == "UNSUPPORTED"
    assert payload["qbox_allowed"] is True
    assert payload["tuple"] == {"ecam": "0x10040000000", "esr_el3": "0x00000000be000211", "elr_el3": "0xffff8000807d08f0", "endpoint": "0004:00:1f.0"}
    assert payload["claims"] == {"physical_its_delivery": False, "endpoint_enumeration": False, "qbox_equivalence": False}
    jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(payload)


@pytest.mark.parametrize(
    ("name", "old", "new"),
    [
        ("secure.log", "be000211", "be000212"),
        ("ns.log", "PCI host bridge to bus 0004:00", "PCI host bridge to bus 0004:00\n0004:00:1f.0"),
        ("README.md", "immutable test-fixture", "mutable test-fixture"),
        ("source-identity.json", "28b63033", "00000000"),
    ],
)
def test_fixture_hash_gate_rejects_mutated_recorded_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, old: str, new: str) -> None:
    # Given: a private materialization of the immutable fixture.
    copied = tmp_path / "fixture"
    shutil.copytree(FIXTURE, copied)
    target = copied / name
    target.write_text(target.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
    manifest, validator = fixture_modules()
    monkeypatch.setattr(manifest, "FIXTURE_ROOT", copied)
    monkeypatch.setattr(manifest, "MANIFEST_PATH", copied / "manifest.json")
    monkeypatch.setattr(validator, "FIXTURE_ROOT", copied)
    monkeypatch.setattr(validator, "MANIFEST_PATH", copied / "manifest.json")

    # When: the materialized fixture is validated.
    with pytest.raises(getattr(manifest, "ManifestError")):
        validator.validate()



def test_fixture_manifest_rejects_malformed_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    inventory = tmp_path / "inventory"
    shutil.copytree(FIXTURE, inventory)
    manifest, _ = fixture_modules()
    monkeypatch.setattr(manifest, "FIXTURE_ROOT", inventory)
    monkeypatch.setattr(manifest, "MANIFEST_PATH", inventory / "manifest.json")
    loaded = manifest.load_manifest(inventory / "manifest.json")
    (inventory / "unhashed.txt").write_text("unhashed", encoding="utf-8")
    with pytest.raises(getattr(manifest, "ManifestError")):
        manifest.verify_inputs(loaded)

    copied = tmp_path / "fixture"
    shutil.copytree(FIXTURE, copied)
    (copied / "manifest.json").write_text("{", encoding="utf-8")
    monkeypatch.setattr(manifest, "FIXTURE_ROOT", copied)
    monkeypatch.setattr(manifest, "MANIFEST_PATH", copied / "manifest.json")
    with pytest.raises(getattr(manifest, "ManifestError")):
        manifest.load_manifest(copied / "manifest.json")
