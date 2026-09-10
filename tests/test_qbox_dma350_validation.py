import importlib.util
from pathlib import Path


path = Path(__file__).resolve().parents[1] / "scripts/test/validate_qbox_dma350.py"
spec = importlib.util.spec_from_file_location("dma350_validation", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def evidence():
    guest = ["APOLLO_DMA350|result=0|artifacts=/tmp/test",
             "APOLLO_DMA350|topology=dedicated|channels=8|status=PASS",
             "APOLLO_DMA350|interrupt=shared|specifiers=8|lines=1|hwirq=311|status=PASS",
             "APOLLO_DMA350|memory=dma0chan4|status=PASS"]
    host = ["ap_dma350 copy channel=0x0 source=0x80000000 dest=0x80001000 bytes=0x40 src_trigger=-1 dest_trigger=-1 status=done"]
    host.append("ap_dma350 fill channel=0x0 source=0x0 dest=0x80001000 bytes=0x40 src_trigger=-1 dest_trigger=-1 status=done")
    for kind, count, base, register, first in (
        ("spi", 2, 0x30160000, 0x60, 0),
        ("uart", 2, 0x301A0000, 0, 4),
    ):
        for port in range(count):
            address = base + port * 0x10000 + register
            for size in ((4096, 3) if kind == "spi" else (64,)):
                host.append(f"ap_dma350 copy channel={first + 2 * port:#x} source=0x80000000 dest={address:#x} bytes={size:#x} src_trigger=-1 dest_trigger={first + 2 * port} status=done")
                status = "done" if kind == "spi" else "stopped"
                host.append(f"ap_dma350 copy channel={first + 2 * port + 1:#x} source={address:#x} dest=0x80001000 bytes={size:#x} src_trigger={first + 2 * port + 1} dest_trigger=-1 status={status}")
            if kind == "uart":
                for length in (17, 128, 512, 4099):
                    guest.append(f"APOLLO_DMA350|uart={base + port * 0x10000:x}->{base + (port ^ 1) * 0x10000:x}|bytes={length}|irq_after=1|status=PASS")
            else:
                for length in (64, 4099):
                    guest.append(f"APOLLO_DMA350|{kind}={port}|bytes={length}|vmalloc={int(length == 4099)}|status=PASS")
    return "\n".join(guest), "\n".join(host)


def test_complete_evidence_passes():
    assert module.evaluate(*evidence())["status"] == "PASS"


def test_renamed_primary_dma_instance_is_accepted():
    guest, host = evidence()
    assert module.evaluate(guest, host.replace("ap_dma350", "dma350_0"))["status"] == "PASS"


def test_pio_only_data_is_not_dma_proof():
    guest, _ = evidence()
    assert module.evaluate(guest, "")["status"] == "FAIL"


def test_missing_rx_direction_is_rejected():
    guest, host = evidence()
    host = "\n".join(line for line in host.splitlines() if "src_trigger=5 " not in line)
    assert module.evaluate(guest, host)["status"] == "FAIL"


def test_bus_error_is_not_hidden_by_successful_operations():
    guest, host = evidence()
    host += "\nap_dma350 copy channel=0x0 source=0x80000000 dest=0x30100010 bytes=0x0 src_trigger=-1 dest_trigger=0 status=error"
    assert module.evaluate(guest, host)["status"] == "FAIL"


def test_guest_failure_is_rejected():
    guest, host = evidence()
    assert module.evaluate(guest.replace("result=0", "result=1"), host)["status"] == "FAIL"


def test_wrong_physical_channel_is_rejected():
    guest, host = evidence()
    assert module.evaluate(guest, host.replace("channel=0x7", "channel=0x1"))["status"] == "FAIL"


def test_excluded_peripheral_dma_is_rejected():
    guest, host = evidence()
    host += "\nap_dma350 copy channel=0x0 source=0x80000000 dest=0x30100010 bytes=0x12 src_trigger=-1 dest_trigger=0 status=done"
    assert module.evaluate(guest, host)["status"] == "FAIL"


def test_pio_fifo_access_without_trigger_is_rejected():
    guest, host = evidence()
    host += "\nap_dma350 copy channel=0x0 source=0x30100010 dest=0x80000000 bytes=0x12 src_trigger=-1 dest_trigger=-1 status=done"
    assert module.evaluate(guest, host)["status"] == "FAIL"


def test_single_command_is_not_scatter_gather_evidence():
    guest, host = evidence()
    host = host.replace("bytes=0x1000", "bytes=0x1003")
    assert module.evaluate(guest, host)["status"] == "FAIL"


def test_per_channel_irqs_are_not_combined_irq_proof():
    guest, host = evidence()
    assert module.evaluate(guest.replace("lines=1", "lines=8"), host)["status"] == "FAIL"


def test_shared_irq_requires_all_channel_specifiers():
    guest, host = evidence()
    assert module.evaluate(guest.replace("specifiers=8", "specifiers=1"), host)["status"] == "FAIL"
