"""Reject incomplete qualification evidence for the SI-owned PMIC migration."""
import importlib.util
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    "si_pmic_validation",
    Path(__file__).resolve().parents[1] / "scripts/test/verify_qbox_si_pmic.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def logs():
    scp = "[TPS6594] begin count=1 before=power\n"
    scp += ("[TPS6594] ready address=0x48 rails=9 gpio=11 "
            "policy=preserve rtc=untouched\n")
    scp += ("[TPS6594] check address=0x48 probe=PASS "
            "rail_config=SKIP gpio_test=SKIP\n")
    scp += "[TPS6594] complete count=1 elapsed_us=2100\n[TPS6594] power-ready\n"
    guest = "APOLLO_SI_PMIC_GUEST|v=1|event=ownership|pmics=0|regulators=0|children=0|status=PASS\n"
    guest += "APOLLO_SI_PMIC_GUEST|v=1|event=rtc|driver=rtc-pl031|count=1|status=PASS\n"
    eeprom = ""
    for client in ("0-0050", "0-0051", "0-0052"):
        guest += f"APOLLO_SI_PMIC_GUEST|v=1|event=eeprom|client={client}|driver=at24|status=PASS\n"
        eeprom += f"APOLLO_I2C_MULTI_SLAVE|v=1|event=restore|client={client}|status=PASS\n"
    guest += "APOLLO_SI_PMIC_GUEST|v=1|event=final|status=PASS|pmics=0|eeproms=3|rtc=pl031\n"
    eeprom += "APOLLO_I2C_MULTI_SLAVE|v=1|event=final|status=PASS|clients=3|rounds=8|bytes=256\n"
    return [scp, guest, eeprom]


def test_complete_evidence(logs):
    result = module.qualify(*logs)
    assert result["status"] == "PASS"
    assert result["rail_configuration"] == result["gpio_test"] == "SKIP"


@pytest.mark.parametrize("index,old,new", [
    (0, "address=0x48", "address=0x60"),
    (0, "rails=9", "rails=8"),
    (0, "probe=PASS", "probe=FAIL"),
    (0, "rail_config=SKIP", "rail_config=PASS"),
    (0, "gpio_test=SKIP", "gpio_test=PASS"),
    (0, "gpio_test=SKIP", ""),
    (0, "policy=preserve", "faults=masked"),
    (0, "policy=preserve", "policy=preserve faults=masked"),
    (0, "probe=PASS", "probe=PASS rail_readback=PASS"),
    (0, "count=1", "count=4"),
    (0, "[TPS6594] check address=0x48", "[TPS6594] check address=0x60"),
    (0, "[TPS6594] check address=0x48", "[TPS6594] omitted address=0x48"),
    (0, "[TPS6594] power-ready", ""),
    (0, "elapsed_us=2100", "elapsed_us=bad"),
    (1, "driver=rtc-pl031", "driver=tps6594-rtc"),
    (1, "pmics=0", "pmics=4"),
    (1, "client=0-0052", "client=0-0051"),
    (2, "event=restore", "event=skipped"),
    (2, "rounds=8", "rounds=1"),
])
def test_reject_incomplete_evidence(logs, index, old, new):
    logs[index] = logs[index].replace(old, new)
    assert module.qualify(*logs)["status"] == "FAIL"


def test_reject_early_power(logs):
    logs[0] = "[TPS6594] power-ready\n" + logs[0].replace("[TPS6594] power-ready\n", "")
    assert module.qualify(*logs)["status"] == "FAIL"


def test_reject_early_check(logs):
    lines = logs[0].splitlines()
    lines[1], lines[2] = lines[2], lines[1]
    logs[0] = "\n".join(lines)
    assert module.qualify(*logs)["status"] == "FAIL"


def test_reject_late_check(logs):
    lines = logs[0].splitlines()
    lines.append(lines.pop(2))
    logs[0] = "\n".join(lines)
    assert module.qualify(*logs)["status"] == "FAIL"


def test_explicit_simulated_time_budget(logs):
    assert module.qualify(*logs, max_elapsed_us=2000)["status"] == "FAIL"


def test_empty_evidence():
    assert module.qualify("", "", "")["status"] == "FAIL"


@pytest.mark.parametrize("line", [0, 1, 2, 3, 4])
def test_reject_duplicate_record(logs, line):
    logs[0] += logs[0].splitlines()[line] + "\n"
    assert module.qualify(*logs)["status"] == "FAIL"


def test_reject_failed_then_successful_probe(logs):
    logs[0] = "[TPS6594] failed address=0x48 status=-1\n" + logs[0]
    assert module.qualify(*logs)["status"] == "FAIL"


def test_reject_previous_four_pmic_full_initialization(logs):
    scp = "[TPS6594] begin count=4 before=power\n"
    for address in ("0x48", "0x58", "0x60", "0x68"):
        scp += (f"[TPS6594] ready address={address} rails=9 gpio=11 "
                "faults=masked rtc=untouched\n")
        scp += (f"[TPS6594] check address={address} gpio_test=PASS "
                "gpio_loopback=PASS rail_readback=PASS mask_readback=PASS\n")
    logs[0] = scp + "[TPS6594] complete count=4 elapsed_us=2100\n[TPS6594] power-ready\n"
    assert module.qualify(*logs)["status"] == "FAIL"
