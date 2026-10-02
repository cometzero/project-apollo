"""Effective DT changes must fail even when numeric phandles are renumbered."""
from __future__ import annotations

import copy
from pathlib import Path
import shutil
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from scripts.test.apollo_dt_contract import (
    APPROVED_STATUS, ContractError, Node, Resolver, Tree, bank_issues,
    compare_trees, dependency_issues, main, validate_board, validate_soc,
)

ROOT = Path(__file__).resolve().parents[1]
LINUX = ROOT / "hsoc-stack/components/primary_compute/linux"
DTS = LINUX / "arch/arm64/boot/dts/hsoc/apollo-qvp-saturn-v.dts"


def u32(*values: int) -> bytes:
    return struct.pack(f">{len(values)}I", *values)


def compile_dts(text: str, output: Path, *, symbols: bool = False) -> Tree:
    command = ["dtc", "-I", "dts", "-O", "dtb", "-o", str(output)]
    if symbols:
        command.append("-@")
    result = subprocess.run(command, input=text, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return Tree.read(output)


@pytest.fixture(scope="module")
def trees(tmp_path_factory: pytest.TempPathFactory) -> tuple[Tree, Tree]:
    if not shutil.which("dtc"):
        pytest.skip("dtc is required for compiled contract fixtures")
    out = tmp_path_factory.mktemp("dt-reference-contract")
    text = '''/dts-v1/;
/ {
    #address-cells = <2>; #size-cells = <2>;
    numeric = <0x10 0x20>; empty;
    clock0: clock0 { phandle = <0x10>; #clock-cells = <0>; };
    clock2: clock2 { phandle = <0x20>; #clock-cells = <2>; };
    gpio: gpio { phandle = <0x30>; #gpio-cells = <2>; gpio-controller; };
    pins: pins { phandle = <0x40>; };
    dma: dma { phandle = <0x50>; #dma-cells = <1>; };
    inta: inta { phandle = <0x60>; #address-cells = <2>; #interrupt-cells = <3>; interrupt-controller; };
    intb: intb { phandle = <0x70>; #address-cells = <0>; #interrupt-cells = <1>; interrupt-controller; };
    msi: msi { phandle = <0x80>; #msi-cells = <1>; msi-controller; };
    iommu: iommu { phandle = <0x90>; #iommu-cells = <2>; };
    mbox: mbox { phandle = <0xa0>; #mbox-cells = <3>; };
    sound: sound { phandle = <0xb0>; #sound-dai-cells = <0>; };
    mem: mem { phandle = <0xc0>; };
    consumer {
        #address-cells = <1>; #interrupt-cells = <1>;
        clocks = <&clock0>, <&clock2 0x10 0x20>;
        assigned-clock-parents = <0>, <&clock2 0x10 0x20>;
        reset-gpios = <0>, <&gpio 0x10 0x20>;
        dmas = <&dma 0x10>; pinctrl-0 = <&pins>;
        gpio-ranges = <&pins 0x10 0x20 4>;
        msi-parent = <&msi 0x10>;
        msi-map = <0x10 &msi 0x20 0x30>;
        iommu-map = <0x10 &iommu 0x20 0x30>;
        iommus = <&iommu 0x10 0x20>;
        interrupt-parent = <&inta>;
        interrupts = <0x10 0x20 0x30>;
        interrupts-extended = <&inta 0x10 0x20 0x30>, <&intb 0x10>;
        interrupt-map = <1 2 &inta 0x10 0x20 3 4 5>, <6 7 &intb 0x10>;
        mboxes = <&mbox 0x10 0x20 0x30>;
        sound-dai = <&sound>; bitclock-master = <&sound>;
        memory-region = <&mem>; shmem = <&mem>;
    };
    cpus {
        #address-cells = <1>; #size-cells = <0>;
        cpu0: cpu@0 { device_type = "cpu"; reg = <0>; phandle = <0xd0>; };
        cpu1: cpu@1 { device_type = "cpu"; reg = <1>; phandle = <0xe0>; };
        cpu-map { cluster0 { core0 { cpu = <&cpu0>; }; core1 { cpu = <&cpu1>; }; }; };
    };
};'''
    renumbered = text
    for value in range(0x10, 0xF0, 0x10):
        renumbered = renumbered.replace(f"phandle = <0x{value:x}>", f"phandle = <0x{value + 0x100:x}>")
    return compile_dts(text, out / "before.dtb", symbols=True), compile_dts(renumbered, out / "after.dtb", symbols=True)


def test_phandle_renumbering_preserves_mixed_specifiers_and_maps(trees):
    assert compare_trees(*trees) == []
    value = Resolver(trees[1]).references("/consumer", "interrupt-map", trees[1].nodes["/consumer"].properties["interrupt-map"])
    assert value == (1, 2, ("ref", "/inta"), 0x10, 0x20, 3, 4, 5, 6, 7, ("ref", "/intb"), 0x10)
    # These map formats are fixed 4-cell tuples even for a 2-cell IOMMU provider.
    assert Resolver(trees[1]).references("/consumer", "iommu-map", trees[1].nodes["/consumer"].properties["iommu-map"]) == (0x10, ("ref", "/iommu"), 0x20, 0x30)


@pytest.mark.parametrize("property_name,index", [
    ("clocks", 2), ("reset-gpios", 2), ("gpio-ranges", 1), ("msi-map", 2),
    ("iommu-map", 3), ("interrupt-map", 3), ("interrupts", 1), ("dmas", 1),
    ("iommus", 1), ("mboxes", 2), ("interrupts-extended", 2),
])
def test_numeric_argument_equal_to_phandle_is_not_normalized(trees, property_name, index):
    changed = copy.deepcopy(trees[1])
    prop = bytearray(changed.nodes["/consumer"].properties[property_name])
    struct.pack_into(">I", prop, index * 4, 0x1234)
    changed.nodes["/consumer"].properties[property_name] = bytes(prop)
    assert f"changed property: /consumer:{property_name}" in compare_trees(trees[0], changed)


def test_unknown_numeric_property_stays_byte_exact(trees):
    changed = copy.deepcopy(trees[1])
    changed.nodes["/"].properties["numeric"] = u32(0x110, 0x120)
    assert "changed property: /:numeric" in compare_trees(trees[0], changed)


def test_redirected_phandle_target_is_detected(trees):
    changed = copy.deepcopy(trees[1])
    changed.nodes["/consumer"].properties["memory-region"] = u32(0x140)
    assert "changed property: /consumer:memory-region" in compare_trees(trees[0], changed)


@pytest.mark.parametrize("property_name", ["clocks", "gpio-ranges", "msi-map", "iommu-map", "interrupt-map", "mboxes"])
def test_truncated_reference_tuple_is_rejected(trees, property_name):
    changed = copy.deepcopy(trees[1])
    changed.nodes["/consumer"].properties[property_name] = changed.nodes["/consumer"].properties[property_name][:-4]
    with pytest.raises(ContractError, match="truncated"):
        compare_trees(trees[0], changed)


def test_missing_provider_cells_and_dangling_reference_are_rejected(trees):
    changed = copy.deepcopy(trees[1])
    del changed.nodes["/dma"].properties["#dma-cells"]
    with pytest.raises(ContractError, match="missing provider #dma-cells"):
        compare_trees(trees[0], changed)
    changed.nodes["/consumer"].properties["dmas"] = u32(0xDEAD, 0)
    with pytest.raises(ContractError, match="unresolved phandle"):
        compare_trees(trees[0], changed)


def test_cpu_order_missing_node_and_boolean_presence_are_not_ignored(trees):
    changed = copy.deepcopy(trees[1])
    changed.nodes["/cpus"].children[:2] = changed.nodes["/cpus"].children[1::-1]
    assert "changed CPU declaration order: /cpus" in compare_trees(trees[0], changed)
    changed = copy.deepcopy(trees[1])
    del changed.nodes["/"].properties["empty"]
    assert "missing property: /:empty" in compare_trees(trees[0], changed)
    changed = copy.deepcopy(trees[1])
    changed.nodes["/unrelated"] = Node("/unrelated")
    assert "added node: /unrelated" in compare_trees(trees[0], changed)


def test_only_approved_absent_to_okay_status_is_equivalent(trees):
    before, after = copy.deepcopy(trees)
    path = next(iter(APPROVED_STATUS))
    before.nodes[path] = Node(path)
    after.nodes[path] = Node(path, {"status": b"okay\0"})
    assert compare_trees(before, after) == []
    after.nodes[path].properties["status"] = b"disabled\0"
    assert f"added property: {path}:status" in compare_trees(before, after)
    before.nodes[path].properties["status"] = b"okay\0"
    assert f"added property: {path}:status" in compare_trees(before, after)
    after.nodes[path].properties["status"] = b"ok\0"
    assert compare_trees(before, after)
    after.nodes[path].properties["status"] = b"okay\0"
    after.nodes["/consumer"].properties["status"] = b"okay\0"
    assert "added property: /consumer:status" in compare_trees(before, after)


def test_symbol_addition_requires_explicit_policy_and_removal_always_fails(trees):
    changed = copy.deepcopy(trees[1])
    changed.nodes["/__symbols__"].properties["additional"] = b"/consumer\0"
    assert "added property: /__symbols__:additional" in compare_trees(trees[0], changed)
    assert compare_trees(trees[0], changed, allow_added_symbols=True) == []
    del changed.nodes["/__symbols__"].properties["clock0"]
    assert "missing property: /__symbols__:clock0" in compare_trees(trees[0], changed, allow_added_symbols=True)


def test_efi_runtime_policy_preserves_presence_width_and_bootargs(trees):
    before, after = copy.deepcopy(trees)
    for tree, value in ((before, 1), (after, 2)):
        tree.nodes["/chosen"] = Node("/chosen", {"kaslr-seed": u32(0, value), "bootargs": b"console=ttyAMA0\0"})
    assert compare_trees(before, after) == ["changed property: /chosen:kaslr-seed"]
    assert compare_trees(before, after, ignore_efi_runtime=True) == []
    after.nodes["/chosen"].properties["bootargs"] = b"console=ttyS0\0"
    assert "changed property: /chosen:bootargs" in compare_trees(before, after, ignore_efi_runtime=True)
    after.nodes["/chosen"].properties["kaslr-seed"] = u32(3)
    with pytest.raises(ContractError, match="runtime value width"):
        compare_trees(before, after, ignore_efi_runtime=True)
    del after.nodes["/chosen"].properties["kaslr-seed"]
    assert "missing property: /chosen:kaslr-seed" in compare_trees(before, after, ignore_efi_runtime=True)


@pytest.fixture(scope="module")
def board(tmp_path_factory: pytest.TempPathFactory) -> Tree:
    if not DTS.is_file() or not shutil.which("cpp") or not shutil.which("dtc"):
        pytest.skip("Apollo kernel DTS and CPP/DTC are required")
    out = tmp_path_factory.mktemp("apollo-board-contract")
    result = subprocess.run(["cpp", "-undef", "-nostdinc", "-x", "assembler-with-cpp", "-I", str(LINUX / "include"), "-I", str(LINUX / "scripts/dtc/include-prefixes"), str(DTS)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return compile_dts(result.stdout, out / "board.dtb")


def test_canonical_board_composes_all_dependencies(board):
    assert validate_board(board) == []


@pytest.mark.parametrize("provider", [
    "/soc/gpio@301e0000", "/soc/dma-controller@31000000", "/soc/gpio@40750000",
    "/soc/si_remoteproc", "/soc/mailbox@400e0000", "/reserved-memory/vdev0buffer@160000",
])
def test_board_missing_enable_fails_provider_or_parent_contract(board, provider):
    changed = copy.deepcopy(board)
    changed.nodes[provider].properties["status"] = b"disabled\0"
    assert f"Saturn-V required node unavailable: {provider}" in validate_board(changed)
    if provider != "/soc/si_remoteproc":
        assert any("unavailable dependency" in issue for issue in dependency_issues(changed))


def test_gpio_middle_bank_removal_and_bank_disable_are_detected(board):
    changed = copy.deepcopy(board)
    bank = "/soc/gpio@301e0000/gpio@7"
    changed.nodes["/soc/gpio@301e0000"].children.remove(bank)
    del changed.nodes[bank]
    assert any("bank topology/order" in issue for issue in bank_issues(changed, Resolver(changed)))
    assert any("missing node: " + bank == issue for issue in compare_trees(board, changed))
    changed = copy.deepcopy(board)
    changed.nodes[bank].properties["status"] = b"disabled\0"
    assert f"disabled GPIO bank: {bank}" in validate_board(changed)


@pytest.mark.parametrize("path,property_name,index", [
    ("/memory@80000000", "reg", 4),
    ("/soc/spi@30160000", "dmas", 1),
    ("/soc/dma-controller@31000000", "interrupts", 1),
])
def test_real_board_high_dram_irq_and_dma_request_mutations_fail(board, path, property_name, index):
    changed = copy.deepcopy(board)
    value = bytearray(changed.nodes[path].properties[property_name])
    struct.pack_into(">I", value, index * 4, 0)
    changed.nodes[path].properties[property_name] = bytes(value)
    # SPI TX request is already zero; change it to another valid channel.
    if property_name == "dmas":
        value = bytearray(value)
        struct.pack_into(">I", value, index * 4, 1)
        changed.nodes[path].properties[property_name] = bytes(value)
    assert f"changed property: {path}:{property_name}" in compare_trees(board, changed)


def test_soc_rejects_board_population_and_enabled_optional(board):
    issues = validate_soc(board)
    assert any("board/VP node leaked" in issue for issue in issues)
    assert any("SoC optional node must exist and be disabled" in issue for issue in issues)


def test_parser_and_cli_fail_closed_for_corrupt_fdt(tmp_path):
    broken = tmp_path / "broken.dtb"
    broken.write_bytes(b"not a flattened tree")
    assert main(["compare", str(broken), str(broken)]) == 1
    with pytest.raises(ContractError, match="header"):
        Tree.parse(broken.read_bytes())


def test_prepared_disabled_pmu_refs_require_source_and_stay_path_exact(trees):
    sources = copy.deepcopy(trees)
    prepared = copy.deepcopy(trees)
    for i, tree in enumerate(prepared):
        tree.nodes["/dsu-pmu-0"] = Node("/dsu-pmu-0", {
            "compatible": b"arm,dsu-pmu\0", "status": b"disabled\0",
            "cpus": u32(0xD0 + i * 0x100, 0xE0 + i * 0x100),
        })
        tree.nodes["/cpus"].children.remove("/cpus/cpu@1")
        del tree.nodes["/cpus/cpu@1"]
        del tree.nodes["/cpus/cpu-map/cluster0/core1"]
        del tree.nodes["/__symbols__"].properties["cpu1"]
    with pytest.raises(ContractError, match="unresolved phandle"):
        compare_trees(*prepared)
    assert compare_trees(*prepared, baseline_reference=sources[0], candidate_reference=sources[1]) == []
    prepared[1].nodes["/dsu-pmu-0"].properties["status"] = b"okay\0"
    with pytest.raises(ContractError, match="unresolved phandle"):
        compare_trees(*prepared, baseline_reference=sources[0], candidate_reference=sources[1])


def test_source_companions_never_hide_other_disabled_dangling_references(trees):
    before, after = copy.deepcopy(trees)
    after.nodes["/consumer"].properties["status"] = b"disabled\0"
    del after.nodes["/dma"]
    with pytest.raises(ContractError, match="unresolved phandle"):
        compare_trees(before, after, baseline_reference=trees[0], candidate_reference=trees[1])
    with pytest.raises(ContractError, match="both source DTB companions"):
        compare_trees(before, after, baseline_reference=trees[0])


def test_duplicate_phandles_and_inconsistent_aliases_fail_closed(trees):
    changed = copy.deepcopy(trees[1])
    changed.nodes["/clock2"].properties["phandle"] = u32(0x110)
    with pytest.raises(ContractError, match="duplicate phandle"):
        Resolver(changed)
    changed = copy.deepcopy(trees[1])
    changed.nodes["/clock0"].properties["linux,phandle"] = u32(0x999)
    with pytest.raises(ContractError, match="inconsistent phandle aliases"):
        Resolver(changed)


def test_linux_board_cannot_claim_si_owned_pmic(board):
    changed = copy.deepcopy(board)
    path = "/soc/i2c@30100000/pmic@48"
    changed.nodes[path] = Node(path, {"compatible": b"ti,tps6594-q1\0"})
    assert f"SI-owned PMIC must not be populated by Linux: {path}" in validate_board(changed)
