"""Descriptor evidence must catch semantic changes hidden by Lua file moves."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys

import pytest

from scripts.test.apollo_lua_descriptor import (
    DescriptorError, descriptor_differences, evaluate_modules, normalize_file_paths,
    plain_descriptor,
)
from scripts.test.apollo_ap_map_lua import load_module_graph
from scripts.test.apollo_lua_contracts import contracts
from scripts.test.validate_qbox_apollo_fvp_full_map import CHECKS


ROOT = Path(__file__).resolve().parents[1]
APOLLO = ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo"
pytestmark = pytest.mark.skipif(not any(shutil.which(name) for name in
    ("lua5.4", "lua5.3", "lua", "luajit")), reason="Lua interpreter unavailable")


def evaluate(source, **kwargs):
    return evaluate_modules({"apollo-qvp.lua": source}, **kwargs)


@pytest.mark.parametrize("left,right", [
    ('platform={[1]="value"}', 'platform={["1"]="value"}'),
    ('platform={enabled=false}', 'platform={}'),
    ('platform={ports={}}', 'platform={}'),
    ('platform={value=1}', 'platform={value="1"}'),
    ('platform={reset={bind="&a.reset;&b.reset"}}',
     'platform={reset={bind="&b.reset;&a.reset"}}'),
])
def test_typed_comparison_preserves_keys_absence_values_and_reset_order(left, right):
    before = evaluate(left)["descriptor"]
    after = evaluate(right)["descriptor"]
    assert descriptor_differences(before, after)


def test_table_declaration_order_is_not_semantic():
    assert not descriptor_differences(evaluate('platform={a=1,b=false}')["descriptor"],
                                      evaluate('platform={b=false,a=1}')["descriptor"])


def test_only_file_path_spelling_is_normalized():
    before = evaluate('platform={bin_file="./hw/../image",bind="&x.reset;&y.reset"}')["descriptor"]
    after = evaluate('platform={bin_file="image",bind="&x.reset;&y.reset"}')["descriptor"]
    assert not descriptor_differences(normalize_file_paths(before), normalize_file_paths(after))
    changed = evaluate('platform={bin_file="image",bind="&y.reset;&x.reset"}')["descriptor"]
    assert descriptor_differences(normalize_file_paths(before), normalize_file_paths(changed))


@pytest.mark.parametrize("source", [
    'platform={bad=function() end}', 'platform={};platform.self=platform',
    'platform={bad=0/0}', 'os.execute("false")', 'require("os")',
    'io.open("/etc/passwd")', 'dofile("../outside.lua")',
])
def test_invalid_or_unsafe_evaluation_fails_closed(source):
    with pytest.raises(DescriptorError):
        evaluate(source)


def test_environment_is_explicit_and_repeatable(monkeypatch):
    monkeypatch.setenv("QBOX_TEST_PRIVATE", "host-value")
    source = 'platform={injected=os.getenv("QBOX_TEST_PRIVATE")}'
    assert plain_descriptor(evaluate(source)["descriptor"]) == {}
    assert plain_descriptor(evaluate(source, environment={"QBOX_TEST_PRIVATE": "chosen"})["descriptor"]) == {"injected": "chosen"}
    assert plain_descriptor(evaluate(source)["descriptor"]) == {}


def test_factory_returned_methods_keep_leaf_function_provenance(tmp_path):
    sources = {
        "apollo-qvp.lua": 'local m=dofile("./soc/domain.lua").create({});platform={};m.define(platform)',
        "soc/domain.lua": '''local dir=debug.getinfo(1,"S").source:sub(2):match("(.*/)")
local vp_dir=dir.."../vp/"
local leaf=dofile(vp_dir.."leaf.lua")
return {create=function(ctx) return leaf.create(ctx) end}''',
        "vp/leaf.lua": '''return {create=function(ctx)
local m={}; function m.define(p) p.device={moduletype="test"} end; return m end}''',
    }
    for name, text in sources.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    assert set(load_module_graph(tmp_path / "apollo-qvp.lua")) == set(sources)
    result = evaluate_modules(sources)
    assert result["locations"]["platform.device"]["path"] == "./vp/leaf.lua"


def test_every_migrated_full_map_check_has_a_semantic_predicate():
    result = contracts(APOLLO)
    names = {name for checks in CHECKS.values() for name, path, _ in checks
             if path == "APOLLO_DESCRIPTOR"}
    assert names <= result.keys()
    assert all(result[name] for name in names)


def test_full_map_rejects_wrong_effective_irq_after_component_split(tmp_path):
    source_root = tmp_path / "apollo"
    shutil.copytree(APOLLO, source_root)
    source = source_root / "soc/hw-block/ap_compute/map.lua"
    original = source.read_text()
    assert "sys_timer_non_secure = 49;" in original
    source.write_text(original.replace("sys_timer_non_secure = 49;", "sys_timer_non_secure = 50;"))
    result = contracts(source_root)
    assert not result["timer:ap-refclk-ns-spi49"]
    assert result["timer:ap-refclk-secure-spi48"]


@pytest.mark.parametrize("duplicate", [False, True])
def test_compare_cli_rejects_missing_or_duplicate_baseline_cases(tmp_path, duplicate):
    case = {
        "name": "full-ap1", "entrypoint": "apollo-qvp.lua", "environment": {},
        "descriptor": evaluate("platform={}")["descriptor"],
    }
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"cases": [case, case] if duplicate else [case]}))
    (tmp_path / "apollo-qvp.lua").write_text("platform={}")
    output = tmp_path / "comparison.json"
    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/test/compare_apollo_lua_descriptors.py"),
        "compare", "--source-root", str(tmp_path), "--baseline", str(baseline),
        "--output", str(output),
    ], capture_output=True, text=True, timeout=15)
    assert result.returncode != 0
    assert ("duplicate baseline cases" if duplicate else "missing baseline cases") in result.stderr
    assert not output.exists()


def test_full_map_cli_reports_lua_errors_without_losing_the_diagnostic(tmp_path):
    apollo = tmp_path / "platforms/apollo"
    apollo.mkdir(parents=True)
    (apollo / "apollo-qvp-saturn-v.lua").write_text('error("invalid platform fixture")')
    output = tmp_path / "map.json"
    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/test/validate_qbox_apollo_fvp_full_map.py"),
        "--out", str(output),
    ], env={**os.environ, "QBOX_PLATFORM_DIR": str(tmp_path)},
        capture_output=True, text=True, timeout=15)
    assert result.returncode == 1
    assert "FAIL descriptor:evaluation:" in result.stderr
    assert "invalid platform fixture" in result.stderr
    assert "Traceback" not in result.stderr
    assert json.loads(output.read_text())["passed"] is False
