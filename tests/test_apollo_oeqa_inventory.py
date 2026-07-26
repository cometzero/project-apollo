from __future__ import annotations

import ast
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
    / "lib/oeqa/runtime/cases"
)
DISTRO = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
    / "conf/distro/auto-ad-nexios.conf"
)
SUITES = ROOT / "scripts/validation/suites.json"

GUIDE_CASE_COUNTS = {
    "test_00_fvp_boot": 1,
    "test_00_rse_boot": 2,
    "test_00_si_cl0_boot": 1,
    "test_00_si_cl1_boot": 2,
    "test_00_systemd_boot": 1,
    "test_00_tfa_secure_partition_boot": 1,
    "test_00_uboot_boot": 1,
    "test_20_si_cl0_diagnostics": 2,
    "test_21_si_cl0_pfdi": 4,
    "test_22_si_cl0_smcf": 4,
    "test_30_si_cl1_pfdi": 16,
    "test_31_si_cl1_hipc": 10,
    "test_40_tfa_cpu_topology": 1,
    "test_41_tfa_ras": 9,
    "test_60_linux_connectivity": 2,
    "test_61_linux_dsu": 1,
    "test_62_linux_cpu_topology": 1,
    "test_63_linux_fvp_devices": 5,
    "test_64_linux_pfdi": 4,
    "test_65_linux_crypto": 1,
    "test_71_power_cpuidle": 8,
    "test_72_power_cpufreq": 10,
    "test_73_power_mbpp": 9,
    "test_80_trusted_services": 4,
}
APOLLO_EXTRA_MODULES = {
    "test_00_apollo_uki_boot",
    "test_00_linux_boot",
    "test_00_safety_boot",
    "test_70_power_scmi",
}
ALLOWED_PREFIXES = {
    "00",
    "10",
    "20",
    "21",
    "22",
    "30",
    "31",
    "40",
    "41",
    "50",
    "60",
    "61",
    "62",
    "63",
    "64",
    "65",
    "70",
    "71",
    "72",
    "73",
    "80",
}


def _classes(module: str) -> list[ast.ClassDef]:
    tree = ast.parse((CASES / f"{module}.py").read_text(encoding="utf-8"))
    return [node for node in tree.body if isinstance(node, ast.ClassDef)]


def _test_methods(module: str) -> list[tuple[str, ast.FunctionDef]]:
    methods = []
    for class_node in _classes(module):
        methods.extend(
            (class_node.name, node)
            for node in class_node.body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test")
        )
    return methods


def _dependency_values(method: ast.FunctionDef) -> list[str] | None:
    for decorator in method.decorator_list:
        if not isinstance(decorator, ast.Call):
            continue
        if not isinstance(decorator.func, ast.Name):
            continue
        if decorator.func.id != "OETestDepends" or not decorator.args:
            continue
        value = ast.literal_eval(decorator.args[0])
        assert isinstance(value, list)
        assert all(isinstance(item, str) for item in value)
        return value
    return None


def test_validation_guide_inventory_has_100_cases() -> None:
    observed = {
        module: len(_test_methods(module))
        for module in GUIDE_CASE_COUNTS
    }

    assert observed == GUIDE_CASE_COUNTS
    assert sum(observed.values()) == 100


def test_modules_follow_domain_prefixes_and_exclude_virtualization() -> None:
    modules = {
        path.stem
        for path in CASES.glob("test_*.py")
        if path.stem in GUIDE_CASE_COUNTS or path.stem in APOLLO_EXTRA_MODULES
    }

    assert modules == set(GUIDE_CASE_COUNTS) | APOLLO_EXTRA_MODULES
    for module in modules:
        match = re.fullmatch(r"test_(\d+)_.*", module)
        assert match is not None
        assert match.group(1) in ALLOWED_PREFIXES
        text = (CASES / f"{module}.py").read_text(encoding="utf-8").lower()
        assert "virtualization" not in text
        assert "xen" not in text


def test_functional_cases_have_resolvable_dependencies() -> None:
    modules = set(GUIDE_CASE_COUNTS) | APOLLO_EXTRA_MODULES
    available = {
        f"{module}.{class_name}.{method.name}"
        for module in modules
        for class_name, method in _test_methods(module)
    }

    for module in sorted(modules):
        if module.startswith("test_00_"):
            continue
        for class_name, method in _test_methods(module):
            dependencies = _dependency_values(method)
            assert dependencies, (
                f"{module}.{class_name}.{method.name} needs an "
                "OETestDepends boot or predecessor dependency"
            )
            missing = sorted(set(dependencies) - available)
            assert not missing, (
                f"{module}.{class_name}.{method.name} has missing "
                f"dependencies: {missing}"
            )


def test_yocto_default_suite_selects_all_apollo_modules() -> None:
    text = DISTRO.read_text(encoding="utf-8")
    selected = set(
        re.findall(
            r"^\s+(test_(?:00|[1-8][0-9])_[A-Za-z0-9_]+)\s+\\$",
            text,
            flags=re.MULTILINE,
        )
    )

    assert set(GUIDE_CASE_COUNTS) | APOLLO_EXTRA_MODULES <= selected
    assert "virtualization" not in " ".join(selected)


def test_runner_suite_selections_include_dependency_modules() -> None:
    dependency_modules: dict[str, set[str]] = {}
    for module in set(GUIDE_CASE_COUNTS) | APOLLO_EXTRA_MODULES:
        dependencies = {
            dependency.split(".", 1)[0]
            for _, method in _test_methods(module)
            for dependency in (_dependency_values(method) or [])
        }
        dependency_modules[module] = dependencies - {module}

    suites = json.loads(SUITES.read_text(encoding="utf-8"))
    for suite_name, suite in suites.items():
        selections = {"all": suite["selectors"], **suite["cases"]}
        for selection_name, selectors in selections.items():
            selected = set(selectors)
            missing = {
                module: sorted(dependencies - selected)
                for module in selected
                for dependencies in [dependency_modules.get(module, set())]
                if dependencies - selected
            }
            assert not missing, (
                f"{suite_name}/{selection_name} misses dependency "
                f"modules: {missing}"
            )


def test_cpufreq_negative_case_does_not_swallow_assertions() -> None:
    methods = {
        method.name: method
        for _, method in _test_methods("test_72_power_cpufreq")
    }
    method = methods["test_update_min_max_scaling_frequencies_negative"]
    caught = {
        handler.type.id
        for handler in ast.walk(method)
        if isinstance(handler, ast.ExceptHandler)
        and isinstance(handler.type, ast.Name)
    }
    calls = {
        node.func.attr
        for node in ast.walk(method)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
    }
    finalizers = [
        node.finalbody
        for node in ast.walk(method)
        if isinstance(node, ast.Try) and node.finalbody
    ]

    assert "AssertionError" not in caught
    assert {"try_write", "assertLessEqual", "assertGreaterEqual"} <= calls
    assert len(finalizers) == 2
