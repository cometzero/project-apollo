"""Read-only guest gates must not accept one active unit as all units active."""
from pathlib import Path
import importlib.util
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("inactive,expected", [
    ("none", 0),
    ("sysboot-health.target", 3),
    ("ukiboot-set-success.service", 3),
])
def test_every_ota_acceptance_unit_must_be_active(inactive, expected):
    source = (ROOT / "scripts/autosd_demo/ota_check_guest.sh").read_text()
    start = source.index("require_active_units() {")
    function = source[start:source.index("\n}\n", start) + 3]
    script = '''systemctl() {
        test "$1" = is-active || return 2
        if test "$2" = "$INACTIVE"; then echo inactive; return 3; fi
        echo active
    }
    ''' + function + "\nrequire_active_units sysboot-health.target ukiboot-set-success.service\n"
    result = subprocess.run(["bash", "-c", script], env={"INACTIVE": inactive},
                            capture_output=True, text=True, check=False)
    assert result.returncode == expected


@pytest.mark.parametrize("args,expected", [
    (["unsupported", "a" * 64], 2),
    (["good", "not-a-sha256"], 1),
    (["bad", "a" * 63], 1),
])
def test_ota_stage_rejects_invalid_input_before_guest_commands(args, expected):
    result = subprocess.run(
        ["/bin/bash", str(ROOT / "scripts/autosd_demo/ota_stage_guest.sh"), *args],
        env={"PATH": "/nonexistent"}, capture_output=True, text=True, check=False,
    )
    assert result.returncode == expected
    assert "command not found" not in result.stderr


def ota_uart_verifier():
    spec = importlib.util.spec_from_file_location(
        "ota_evidence", ROOT / "scripts/autosd_demo/ota_verify_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verify_uart


def complete_ota_uart():
    log = "Test booting slot A, tries_remaining: 7\nLoading UKI from partition ukiboot_a\n"
    log += "Loading UKI from partition ukiboot_b\n"
    for tries in range(7, 0, -1):
        log += f"Test booting slot A, tries_remaining: {tries}\nLoading UKI from partition ukiboot_a\n"
        log += "Failed to start sysboot-check@failure.service - System boot check - failure.\n"
        log += "systemd-shutdown[1]: Rebooting.\n"
    return log + "Loading UKI from partition ukiboot_b\n"


def test_full_automatic_rollback_uart():
    assert ota_uart_verifier()(complete_ota_uart())["bad_tries"] == [7, 6, 5, 4, 3, 2, 1]


@pytest.mark.parametrize("mutation", ["missing_failure", "wrong_retry", "no_recovery"])
def test_incomplete_rollback_uart_is_not_pass(mutation):
    text = complete_ota_uart()
    if mutation == "missing_failure":
        text = text.replace("System boot check - failure.", "Other failure.", 1)
    elif mutation == "wrong_retry":
        text = text.replace("tries_remaining: 3", "tries_remaining: 4")
    else:
        text = text.rsplit("Loading UKI from partition ukiboot_b", 1)[0]
    with pytest.raises(ValueError):
        ota_uart_verifier()(text)
