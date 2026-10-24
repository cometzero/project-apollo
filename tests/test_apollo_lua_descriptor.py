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
    plain_descriptor, evaluate_source,
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


@pytest.mark.parametrize("cpu_count", ["4", "16"])
def test_ae_mailbox_peers_and_fmu_fault_reset_routes(cpu_count):
    platform = plain_descriptor(evaluate_source(
        APOLLO, entrypoint="apollo-qvp-saturn-v.lua",
        environment={"QBOX_APOLLO_NUM_CPUS": cpu_count},
    )["descriptor"])
    peers = {}
    for name, device in platform.items():
        if isinstance(device, dict) and device.get("moduletype") == "mhu320ae":
            peers.setdefault(device["pair"], {})[device["frame"]] = device
    assert peers
    for pair in peers.values():
        assert set(pair) == {"pbx", "mbx"}
        for parameter, expected in (("fast_channel_count", 64),
                                    ("fast_channels_per_group", 32),
                                    ("fast_channel_word_bits", 32)):
            assert pair["pbx"][parameter] == pair["mbx"][parameter] == expected
    for name in ("ap_to_si_cl0_ns", "si_cl0_to_ap_ns"):
        assert all(peer["ras_enable"] for peer in peers[name].values())

    gic = platform["ap_gic_multiview"]
    assert gic["backend_multi_view"] and platform["ap_gic"]["has_multi_view"]
    assert gic["backend_socket"]["bind"] == "&ap_gic_backend_router.target_socket"
    assert platform["ap_gic"]["dist_iface"]["bind"] == "&ap_gic_backend_router.initiator_socket"
    assert platform["ap_gic"]["dist_iface"]["address"] == gic["backend_dist_base"] == 0x60000000
    assert gic["view0_dist"]["address"] == 0x20000000
    assert gic["view1_dist"]["address"] == 0x20800000
    assert gic["view1_dist"]["bind"] == "&ap_router.initiator_socket"
    assert gic["view_redist_stride"] == 0x40000
    assert gic["view1_redists"] == {
        "address": 0x20880000, "size": int(cpu_count) * 0x40000,
        "bind": "&ap_router.initiator_socket", "priority": 0,
    }
    for cpu in range(int(cpu_count)):
        raw = platform["ap_gic"][f"redist_iface_{cpu}"]
        assert raw["bind"] == "&ap_gic_backend_router.initiator_socket"
        assert raw["address"] == gic["backend_redist_base"] + cpu * 0x40000
        assert raw["address"] >= 0x61000000
        assert raw["size"] == 0x40000
        assert f"view1_redist_{cpu}" not in gic
        assert gic[f"view0_redist_{cpu}"]["address"] == 0x20080000 + cpu * 0x40000

    assert "mem" not in platform["ap_gic_its"]
    assert gic["its"]["address"] == 0x20840000
    assert gic["its"]["bind"] == "&ap_router.initiator_socket"
    assert gic["backend_its_socket"]["bind"] == "&ap_gic_its.mem"
    assert gic["internal_spi"]["bind"] == "&ap_gic.internal_spi"
    si = platform["si_gic_multiview"]
    assert si["backend_socket"]["bind"] == "&si_gic_backend_router.target_socket"
    assert si["fmu_error_socket"]["bind"] == "&si_cl0_gic_fmu.error_socket"
    for cluster in (0, 1):
        raw = platform[f"si_cl{cluster}_gic"]
        assert raw["has_multi_view"]
        assert raw["dist_iface"]["bind"] == "&si_gic_backend_router.initiator_socket"
    assert platform["si_cl0_ap_ns_mhu_mbx"]["fmu_fault_socket"]["bind"] == "&si_cl0_pc0_cl0_mhu_fmu.error_socket"
    assert platform["host_ap_si_ns_scmi_mhu_mbx"]["fmu_fault_socket"]["bind"] == "&si_cl0_cl0_pc0_mhu_fmu.error_socket"

    leaves = {name: device for name, device in platform.items()
              if isinstance(device, dict) and device.get("moduletype") == "zena_device_fmu"}
    assert len(leaves) == 11
    reset_bindings = [value["bind"] for device in platform.values()
                      if isinstance(device, dict) for value in device.values()
                      if isinstance(value, dict) and "bind" in value
                      and "&si_cl0_fmu.reset_in" in value["bind"]]
    assert reset_bindings
    assert "&ap_gic_multiview.reset" not in platform["ap_cold_reset_fanout"]["reset_out"]["bind"]
    assert all("&ap_gic_multiview.reset" in binding for binding in reset_bindings)
    records = set()
    for name, device in leaves.items():
        assert device["clock_period_ns"] == 8
        assert device["mhu_profile"] == (name != "si_cl0_gic_fmu")
        assert device["fault_socket"]["bind"] == "&si_cl0_fmu.device_fault_socket"
        for key in ("parent_critical_record", "parent_non_critical_record"):
            record = (device["parent_bank"], device[key])
            assert record not in records
            records.add(record)
        for binding in reset_bindings:
            assert binding.index("&" + name + ".reset_in") < binding.index("&si_cl0_fmu.reset_in")

    critical_records = {tuple(map(int, record.split(":")))
                        for record in platform["si_cl0_fmu"]["critical_records"].split(",")}
    assert {(0, record) for record in (0, 2, 4, 6)} <= critical_records
    ni_leaves = {name: device for name, device in platform.items()
                 if isinstance(device, dict) and device.get("moduletype") == "zena_ni710ae_fmu"}
    assert len(ni_leaves) == 6
    for name, device in {**leaves, **ni_leaves}.items():
        assert (device["parent_bank"], device["parent_critical_record"]) in critical_records
        assert (device["parent_bank"], device["parent_non_critical_record"]) not in critical_records
    for name, device in ni_leaves.items():
        assert device["fault_socket"]["bind"] == "&si_cl0_fmu.device_fault_socket"
        assert device.get("critical_vector", 0) == 0
        assert device["parent_bank"] == 1
        assert device["parent_fault_record"] == device["parent_non_critical_record"] + 1
        for key in ("parent_critical_record", "parent_non_critical_record", "parent_fault_record"):
            record = (device["parent_bank"], device[key])
            assert record not in records
            records.add(record)
        for binding in reset_bindings:
            assert binding.index("&" + name + ".reset_in") < binding.index("&si_cl0_fmu.reset_in")


def test_full_map_rejects_wrong_effective_irq_after_component_split(tmp_path):
    source_root = tmp_path / "apollo"
    shutil.copytree(APOLLO, source_root)
    source = source_root / "soc/hw-block/ap_compute/system.lua"
    original = source.read_text()
    assert "local AP_SYS_TIMER_NON_SECURE_SPI = 49" in original
    source.write_text(original.replace(
        "local AP_SYS_TIMER_NON_SECURE_SPI = 49",
        "local AP_SYS_TIMER_NON_SECURE_SPI = 50", 1))
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
