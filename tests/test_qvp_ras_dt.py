"""Compile the QVP DTs and check the TF-A -> Linux RAS delivery contract."""
from pathlib import Path
import re
import shutil
import struct
import subprocess

import pytest

from scripts.test.apollo_dt_contract import Tree, cells


ROOT = Path(__file__).resolve().parents[1]
LINUX = ROOT / "hsoc-stack/components/primary_compute/linux"
TFA_QVP = ROOT / "hsoc-stack/components/primary_compute/trusted-firmware-a/plat/arm/board/automotive_rd/platform/apollo_qvp"
MODEL = ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/soc/hw-block/ap_compute/memory.lua"
CPER_BASE, CPER_SIZE = 0xFFA00000, 0x100000
RAS_PATH = "/soc/ras-ffh@ffa00000"
BUFFER_PATH = "/reserved-memory/cper@ffa00000"


@pytest.fixture(scope="module", params=(16, 4), ids=("16-cpus", "4-cpus"))
def qvp_tree(request, tmp_path_factory):
    if not all(shutil.which(tool) for tool in ("cpp", "dtc")):
        pytest.skip("CPP and DTC are required for the compiled RAS DT contract")
    count = request.param
    leaf = "apollo-qvp-saturn-v" + ("-4cpus" if count == 4 else "")
    source = LINUX / f"arch/arm64/boot/dts/hsoc/{leaf}.dts"
    preprocessed = subprocess.run(
        ["cpp", "-undef", "-nostdinc", "-x", "assembler-with-cpp",
         "-I", str(LINUX / "include"), "-I", str(LINUX / "scripts/dtc/include-prefixes"),
         str(source)], check=True, text=True, capture_output=True,
    )
    output = tmp_path_factory.mktemp(f"qvp-ras-{count}") / "board.dtb"
    result = subprocess.run(
        ["dtc", "-I", "dts", "-O", "dtb", "-o", str(output)],
        input=preprocessed.stdout, text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    tree = Tree.read(output)
    assert sum(node.properties.get("device_type") == b"cpu\0" and tree.available(path)
               for path, node in tree.nodes.items()) == count
    return tree


def test_qvp_registers_one_irq_driven_linux_cper_consumer(qvp_tree):
    consumers = [path for path, node in qvp_tree.nodes.items()
                 if b"arm,ras-ffh" in node.properties.get("compatible", b"").split(b"\0")]
    assert consumers == [RAS_PATH]
    assert qvp_tree.available(RAS_PATH)
    consumer = qvp_tree.nodes[RAS_PATH].properties
    buffer = qvp_tree.nodes[BUFFER_PATH].properties
    expected = struct.pack(">QQ", CPER_BASE, CPER_SIZE)
    assert consumer["reg"] == buffer["reg"] == expected
    assert "no-map" in buffer
    assert consumer["memory-region"] == buffer["phandle"]
    # TF-A signals GIC INTID 89, represented as SPI index 57 in a DT.
    assert cells(consumer["interrupts"], RAS_PATH) == (0, 57, 1)
    assert "poll-interval" not in consumer
    assert "arm,sea-notify" not in consumer


def test_qvp_cper_window_does_not_alias_another_device_or_memory_region(qvp_tree):
    end = CPER_BASE + CPER_SIZE
    for path, node in qvp_tree.nodes.items():
        parent = path.rsplit("/", 1)[0]
        candidate = (parent in ("/soc", "/reserved-memory")
                     or node.properties.get("device_type") == b"memory\0")
        if not candidate or path in (RAS_PATH, BUFFER_PATH) or "reg" not in node.properties:
            continue
        # These root/simple-bus regions use two address and two size cells.
        for base, size in struct.iter_unpack(">QQ", node.properties["reg"]):
            assert base + size <= CPER_BASE or base >= end, f"CPER overlaps {path}"


def test_qvp_ras_dt_window_and_irq_match_existing_firmware_and_model():
    platform = (TFA_QVP / "include/platform_def.h").read_text()
    ras = (TFA_QVP / "ras/include/apollo_qvp_ras.h").read_text()
    memory = MODEL.read_text()
    for macro, expected in (("BASE", CPER_BASE), ("SIZE", CPER_SIZE)):
        firmware = re.search(rf"#define\s+APOLLO_QVP_CPER_BUF_{macro}\s+UL\((0x[0-9A-Fa-f]+)\)", platform)
        model = re.search(rf"local AP_CPER_{macro} = (0x[0-9A-Fa-f]+)", memory)
        assert firmware and model
        assert int(firmware[1], 16) == int(model[1], 16) == expected
    irq = re.search(r"#define\s+ERROR_NOTIFICATION_IRQ\s+(\d+)U", ras)
    assert irq and int(irq[1]) == 32 + 57
