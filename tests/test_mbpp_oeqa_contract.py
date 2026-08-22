from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases"
    / "test_73_power_mbpp.py"
)


def _mbpp_class() -> ast.ClassDef:
    tree = ast.parse(CASE.read_text(encoding="utf-8"), filename=str(CASE))
    return next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "MBPPTest"
    )


def test_mbpp_oeqa_has_nine_ordered_assertions_and_unconditional_cleanup() -> None:
    case = _mbpp_class()
    methods = {
        node.name: node for node in case.body if isinstance(node, ast.FunctionDef)
    }

    assert tuple(sorted(name for name in methods if name.startswith("test_"))) == tuple(
        f"test_{index:02d}_{suffix}"
        for index, suffix in (
            (1, "script_exists_and_is_executable"),
            (2, "help_and_list"),
            (3, "dump_initial_then_set_parking_and_verify"),
            (4, "idempotent_all_profiles"),
            (5, "case_insensitive_all_profiles"),
            (6, "invalid_profile_selection"),
            (7, "toggle_all_modes"),
            (8, "guard_when_not_all_cores_online"),
            (9, "set_governor_to_default"),
        )
    )
    assert "tearDownClass" in methods


def test_mbpp_oeqa_never_converts_contract_failures_to_skips_or_warnings() -> None:
    tree = ast.parse(CASE.read_text(encoding="utf-8"), filename=str(CASE))

    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert not any(
        isinstance(call.func, ast.Attribute) and call.func.attr == "skipTest"
        for call in calls
    )
    assert not any(
        isinstance(call.func, ast.Attribute) and call.func.attr == "warn"
        for call in calls
    )
