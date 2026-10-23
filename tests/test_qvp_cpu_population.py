"""The kernel, UKI and QBox manifest must describe the same AP population."""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

import pytest

from scripts.test.apollo_dt_contract import Tree, compare_trees, dependency_issues


ROOT = Path(__file__).resolve().parents[1]
LINUX = ROOT / "hsoc-stack/components/primary_compute/linux"
BSP = ROOT / "hsoc-stack/yocto/meta-hsoc-bsp"
PRODUCT = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
DT_NAMES = {4: "apollo-qvp-saturn-v-4cpus.dtb", 16: "apollo-qvp-saturn-v.dtb"}


@pytest.fixture(scope="module")
def population_trees(tmp_path_factory):
    if not shutil.which("cpp") or not shutil.which("dtc"):
        pytest.skip("CPP/DTC are required for compiled CPU topology checks")
    directory = tmp_path_factory.mktemp("qvp-cpu-populations")
    trees = {}
    for count, name in DT_NAMES.items():
        source = LINUX / "arch/arm64/boot/dts/hsoc" / name.replace(".dtb", ".dts")
        cpp = subprocess.run(
            ["cpp", "-undef", "-nostdinc", "-x", "assembler-with-cpp",
             "-I", str(LINUX / "include"), str(source)],
            capture_output=True, text=True,
        )
        assert cpp.returncode == 0, cpp.stderr
        output = directory / name
        dtc = subprocess.run(
            ["dtc", "-I", "dts", "-O", "dtb", "-o", str(output)],
            input=cpp.stdout, capture_output=True, text=True,
        )
        assert dtc.returncode == 0, dtc.stderr
        trees[count] = Tree.read(output)
    return trees


@pytest.mark.parametrize("count", [4, 16])
def test_compiled_cpu_population_has_complete_cluster_dependencies(population_trees, count):
    tree = population_trees[count]
    cpus = [node for node in tree.nodes.values()
            if node.properties.get("device_type") == b"cpu\0"]
    assert len(cpus) == count
    assert [struct.unpack(">Q", node.properties["reg"])[0] for node in cpus] == [
        (cpu // 4) * 0x10000 + (cpu % 4) * 0x100 for cpu in range(count)
    ]
    assert len(tree.nodes["/cpus/cpu-map"].children) == count // 4
    assert {path for path in tree.nodes if re.fullmatch(r"/cpus/l3-cache\d+", path)} == {
        f"/cpus/l3-cache{cluster}" for cluster in range(count // 4)
    }
    assert {path for path in tree.nodes if path.startswith("/dsu-pmu-")} == {
        f"/dsu-pmu-{cluster}" for cluster in range(count // 4)
    }
    assert dependency_issues(tree) == []


def test_four_cpu_variant_only_removes_unpopulated_cluster_nodes(population_trees):
    full, reduced = population_trees[16], population_trees[4]
    prefixes = [
        f"/cpus/cpu@{cluster * 0x10000 + core * 0x100:x}"
        for cluster in range(1, 4) for core in range(4)
    ] + [prefix for cluster in range(1, 4) for prefix in (
        f"/cpus/cpu-map/cluster{cluster}", f"/cpus/l3-cache{cluster}",
        f"/dsu-pmu-{cluster}",
    )]
    removed = {path for path in full.nodes if any(
        path == prefix or path.startswith(prefix + "/") for prefix in prefixes
    )}
    assert set(full.nodes) - set(reduced.nodes) == removed
    assert set(compare_trees(full, reduced)) == {
        *(f"missing node: {path}" for path in removed),
        "changed CPU declaration order: /cpus",
    }


def assignment(path, name):
    match = re.search(rf"^{re.escape(name)} = \"(.*)\"$", path.read_text(), re.MULTILINE)
    assert match is not None, f"missing assignment {name}: {path}"
    return match[1]


@pytest.mark.parametrize("count", [4, 16, 8])
def test_metadata_selects_one_population_for_kernel_uki_and_qbox(count):
    """Only expand a fresh datastore; never start a cooker or parse build config."""
    image = PRODUCT / "recipes-core/images/include/nexios-apollo-qboxboot.inc"
    variables = {
        "PC_CPUS_COUNT": str(count),
        "APOLLO_QVP_DTB": assignment(BSP / "conf/machine/apollo-qvp.conf", "APOLLO_QVP_DTB"),
        "kernel": assignment(BSP / "recipes-kernel/linux/linux-yocto-apollo-qvp.inc",
                             "KERNEL_DEVICETREE:apollo-qvp"),
        "uki": assignment(image, "KERNEL_DEVICETREE:apollo-qvp"),
        "qbox": assignment(image, "QBOX_IMAGES[dtb]"),
    }
    script = """
import json, sys
sys.path.insert(0, sys.argv[1])
import bb.data
import bb.parse
d = bb.data.init()
for key, value in json.load(sys.stdin).items():
    d.setVar(key, value)
try:
    print(json.dumps({key: d.getVar(key) for key in ('kernel', 'uki', 'qbox')}))
except bb.data_smart.ExpansionError as error:
    print(str(error), file=sys.stderr)
    sys.exit(2)
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(ROOT / "layers/poky/bitbake/lib")],
        input=json.dumps(variables), capture_output=True, text=True,
    )
    if count not in DT_NAMES:
        assert result.returncode == 2
        assert "APOLLO_QVP_DTB" in result.stderr and "KeyError" in result.stderr
        return
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "kernel": "hsoc/" + DT_NAMES[count], "uki": DT_NAMES[count], "qbox": DT_NAMES[count],
    }
