"""Reject boot-only, command-echo and missing-interrupt I2S evidence."""

import importlib.util
from pathlib import Path

import pytest


SPEC = importlib.util.spec_from_file_location(
    "verify_qemu_i2s", Path(__file__).resolve().parents[1] / "scripts/test/verify_qemu_i2s.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


def evidence(mode="dma"):
    lines = ["QEMU_I2S_IRQ_BEFORE", " 30: 0 0 0 0 GICv3 390 Level dma1chan0",
             " 31: 0 0 0 0 GICv3 388 Level 30200000.i2s",
             " 32: 0 0 0 0 GICv3 389 Level 30210000.i2s", "QEMU_I2S_IRQ_END"]
    for _ in range(2):
        for tx, rx in (("hw:0,0", "hw:1,1"), ("hw:1,0", "hw:0,1")):
            lines.append(f"I2S_LOOPBACK_PASS playback={tx} capture={rx} "
                         "frames=65536 bytes=262144 format=S16_LE rate=48000 idle=16")
    lines += [f"I2S_DRIVER_TEST_PASS mode={mode}", "QEMU_I2S_IRQ_AFTER",
              " 30: 8 16 0 0 GICv3 390 Level dma1chan0",
              " 31: 8 8 0 0 GICv3 388 Level 30200000.i2s",
              " 32: 8 8 0 0 GICv3 389 Level 30210000.i2s",
              "QEMU_I2S_IRQ_END", "QEMU_I2S_DONE=0"]
    return "\r\n".join(lines) + "\r\n"


@pytest.mark.parametrize("mode", ["dma", "pio"])
def test_requires_sequence_comparison_and_irq_progress(mode):
    result = verify.assess(evidence(mode), mode)
    assert result["status"] == "PASS"
    assert result["interrupt_deltas"]["390"] == 24


@pytest.mark.parametrize("mode", ["dma", "pio"])
def test_rejects_missing_irq_progress(mode):
    text = evidence(mode).replace("8 16 0 0", "0 0 0 0").replace("8 8 0 0", "0 0 0 0")
    assert verify.assess(text, mode)["status"] == "FAIL"


def test_rejects_partial_workload_and_wrong_mode():
    assert verify.assess(evidence().replace("I2S_LOOPBACK_PASS", "FAIL", 1), "dma")["status"] == "FAIL"
    assert verify.assess(evidence(), "pio")["status"] == "FAIL"


def test_rejects_missing_before_snapshot():
    text = evidence().replace("QEMU_I2S_IRQ_BEFORE", "MISSING_BEFORE")
    assert verify.assess(text, "dma")["status"] == "FAIL"


def test_command_echo_cannot_pass():
    assert verify.assess(verify.guest_command().decode(), "dma")["status"] == "FAIL"
    assert b"QEMU_I2S_DONE=0" not in verify.guest_command()
    # The Linux canonical serial input buffer is 4096 bytes.
    assert len(verify.guest_command()) < 4096
