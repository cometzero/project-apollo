"""SPI qualification requires guest FIFO/IRQ/GPIO and firmware ACK evidence."""
import importlib.util
from pathlib import Path
import sys

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts/test'
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location('vmcu_services_verify', SCRIPTS / 'verify_qbox_vmcu_services.py')
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)
sys.path.remove(str(SCRIPTS))

MCU = '''VMCU_INIT result=PASS safety=QSPI0
VMCU_SPI rx=1 ack=1 errors=0 epoch=123 sequence=1 type=7
VMCU_SPI rx=2 ack=2 errors=0 epoch=123 sequence=2 type=6
'''
SI = '''[VMCU_SAFETY] transport=spi
[VMCU_SPI] SYNC epoch=123 queued=28
[VMCU_SPI] READY type=7 seq=1 req=1
[VMCU_SPI] ACK seq=1 count=1 irq=2
[VMCU_SPI] READY type=6 seq=2 req=0
[VMCU_SPI] ACK seq=2 count=2 irq=4
'''
STATUS = 'VMCU_SPI_STATUS frames=2 ack=2 irq=112 req=2 failures=0'


def test_actual_spi_evidence():
    assert module.validate_spi_evidence(MCU, SI, STATUS) == dict(
        frames=2, ack=2, irq=112, req=2, failures=0, matched_frame_types=[6, 7])


@pytest.mark.parametrize('mcu,si,status', [
    ('VMCU_INIT result=PASS', SI, STATUS),
    (MCU, SI.replace('transport=spi', 'transport=uart'), STATUS),
    (MCU, SI.replace('req=0', 'req=1'), STATUS),
    (MCU, SI.replace('seq=2 count=2', 'seq=99 count=2'), STATUS),
    (MCU, SI.replace('irq=2', 'irq=0').replace('irq=4', 'irq=0'), STATUS),
    (MCU.replace('type=6', 'type=7'), SI, STATUS),
    (MCU.replace('errors=0', 'errors=1'), SI, STATUS),
    (MCU, SI, STATUS.replace('irq=112', 'irq=0')),
    (MCU, SI, STATUS.replace('req=2', 'req=0')),
    (MCU, SI, STATUS.replace('failures=0', 'failures=1')),
    (MCU, SI, STATUS.replace('ack=2', 'ack=3')),
    (MCU, SI, 'socket ready'),
])
def test_boot_or_transport_only_cannot_pass(mcu, si, status):
    with pytest.raises(RuntimeError):
        module.validate_spi_evidence(mcu, si, status)


def test_startup_errors_are_recorded_but_no_new_errors_allowed():
    mcu = MCU.replace('errors=0', 'errors=3')
    status = STATUS.replace('failures=0', 'failures=3')
    assert module.validate_spi_evidence(mcu, SI, status, 3)['failures'] == 3
    with pytest.raises(RuntimeError):
        module.validate_spi_evidence(mcu, SI, status.replace('failures=3', 'failures=4'), 3)
    with pytest.raises(RuntimeError):
        module.validate_spi_evidence(mcu, SI, status, 0)
