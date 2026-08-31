from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/test/prepare_qbox_apollo_pcie_irq_profile.py"
HELPER = ROOT / "scripts/test/qbox_apollo_pcie_irq_gic_overlay.py"
SCHEMAS = (
    ROOT / "tests/schemas/apollo-qbox-pcie-irq-profile.schema.json",
    ROOT / "tests/schemas/apollo-qbox-pcie-irq-input.schema.json",
)


def pure_loc(path: Path) -> int:
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def test_profile_builder_and_gic_overlay_helper_fit_module_ceiling() -> None:
    assert pure_loc(BUILDER) <= 250
    assert pure_loc(HELPER) <= 250


def test_gic_overlay_helper_is_hash_bound_by_both_profile_schemas() -> None:
    for schema_path in SCHEMAS:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        inputs = schema["$defs"]["inputs"]
        assert "gic_overlay_module" in inputs["required"]
        assert inputs["properties"]["gic_overlay_module"] == {
            "$ref": "#/$defs/artifact"
        }


def test_builder_exports_hash_bound_gic_overlay_helper_path() -> None:
    spec = importlib.util.spec_from_file_location("profile_split_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.GIC_OVERLAY_MODULE == HELPER.resolve()
