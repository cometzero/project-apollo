"""Shared profile-test fixture and module-loading support."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def materialize_fixture(source: Path) -> str:
    if source.suffix != ".json":
        return source.read_text(encoding="utf-8")
    fixture_root = ROOT / "tests/fixtures/gic720ae/pcie-its"
    mutation = json.loads(source.read_text(encoding="utf-8"))
    text = materialize_fixture(fixture_root / mutation["base"])
    replacements = mutation.get(
        "replacements", [[mutation.get("old"), mutation.get("new")]]
    )
    for replacement in replacements:
        old, new = replacement[0], replacement[1]
        assert old in text
        text = text.replace(old, new, replacement[2] if len(replacement) == 3 else 1)
    return text
