"""Boot-stage assertions using excerpts from QBox UART transcripts."""
from types import SimpleNamespace

import pytest

from .test_runtime_cases import Manager, load_case


CASES = (
    ("rse/boot/test_rse_boot.py", "test_rse_normal_boot_and_ap_power_on", "rse", (
        "[INF] Starting TF-M BL1_1",
        "\x00[INF] Starting TF-M BL1_2",
        "[INF] BL2: Init SCMI comm to SCP succeeded",
        "[INF] BL2: RSE to SCP SCMI power on AP succeeded.",
        "[INF] Jumping to the first image slot",
        "[NOT] Booting TF-M \x1b[1;34mv2.2.2+g27d66d3ed06d\x1b[0m",
    )),
    ("rse/boot/test_rse_boot.py", "test_rse_measured_boot", "rse", (
        "[INF] MeasuredBoot: Extending measurement for sw_type: BL2",
        "[INF] MeasuredBoot: Extending measurement for sw_type: BL_33",
    )),
    ("si_cl0/boot/test_scp_boot.py", "test_scp_boot_and_cmn_discovery", "si_cl0", (
        "[   14.328184] [CMN_CYPRUS] CMN Discovery complete",
        "[   18.028679] [SI0_PLATFORM] SCP started",
        "[   18.047814] [FWK] Module initialization complete!",
    )),
    ("si_cl1/boot/test_zephyr_boot.py", "test_zephyr_boot_and_secondary_cpus", "si_cl1", (
        "*** Booting Zephyr OS build v4.1.0-9-g992228a26f3f ***",
        "Secondary CPU core 1 (MPID:0x10100) is up",
        "Secondary CPU core 2 (MPID:0x10200) is up",
        "Secondary CPU core 3 (MPID:0x10300) is up",
        "uart:~$ \x1b[8D\x1b[J",
    )),
    ("ap/boot/test_tfa_boot.py", "test_tfa_boot_and_normal_world_handoff", "secure", (
        "NOTICE:  BL2: Booting BL31",
        "INFO:    BL31: Initializing runtime services",
        "INFO:    BL31: Preparing for EL3 exit to normal world",
    )),
    ("ap/boot/test_uboot_boot.py", "test_uboot_boot_and_efi_handoff", "ap", (
        "U-Boot 2026.01-rc4 (Oct 01 2026 - 03:39:29 +0000) apollo_qvp",
        "Hit any key to stop autoboot: 0\x1b[K",
        "efi: EFI v2.11 by Das U-Boot",
    )),
    ("ap/boot/test_linux_boot.py", "test_linux_boot_and_userspace_handoff", "ap", (
        "Booting Linux on physical CPU 0x0000000000 [0x410fd890]",
        "Linux version 6.18.5-rt3-yocto-preempt-rt (oe-user@oe-host)",
        "Run /init as init process",
    )),
    ("ap/boot/test_optee_boot.py", "test_optee_primary_and_secondary_cpu_boot", "secure", (
        "I/TC: OP-TEE version: a2a275865d65 (gcc version 14.3.0 (GCC))",
        "I/TC: Primary CPU switching to normal world boot",
        "I/TC: Secondary CPU 1 switching to normal world boot",
        "I/TC: Secondary CPU 2 switching to normal world boot",
        "I/TC: Secondary CPU 3 switching to normal world boot",
    )),
)


@pytest.mark.parametrize("relative,name,domain,lines", CASES)
def test_boot_stage_accepts_uart_transcript_without_commands(relative, name, domain, lines):
    case = load_case(relative)
    marks = {mark.name: mark.args[0] for mark in case.pytestmark}
    assert marks == {"domain": relative.split("/")[0], "category": "boot", "image": "any"}
    manager = Manager(logs={domain: "\r\n".join(lines)})
    getattr(case, name)(SimpleNamespace(mgr=manager))
    assert manager.commands == []


@pytest.mark.parametrize("case,missing", [
    (case, index) for case in CASES for index in range(len(case[3]))
], ids=[f"{case[1]}-line{index}" for case in CASES for index in range(len(case[3]))])
def test_incomplete_boot_stage_fails_even_with_other_stage_logs(case, missing):
    relative, name, domain, lines = case
    logs = {port: "\r\n".join(lines) for port in Manager().logs}
    logs[domain] = "\r\n".join(lines[:missing] + lines[missing + 1:])
    with pytest.raises(AssertionError, match=f"{domain}:"):
        getattr(load_case(relative), name)(SimpleNamespace(mgr=Manager(logs=logs)))


@pytest.mark.parametrize("primary", [0x10000, 0x10100, 0x10200, 0x10300])
def test_zephyr_boot_accepts_each_elected_primary_core(primary):
    from scripts.run.qbox_validation.reuse_bsp import si1_boot_complete

    secondaries = [mpid for mpid in (0x10000, 0x10100, 0x10200, 0x10300) if mpid != primary]
    text = "Booting Zephyr OS build\r\n" + "\r\n".join(
        f"Secondary CPU core {cpu} (MPID:{mpid:#x}) is up"
        for cpu, mpid in enumerate(secondaries, 1)
    ) + "\r\nuart:~$"
    assert si1_boot_complete(text)
    case = load_case("si_cl1/boot/test_zephyr_boot.py")
    case.test_zephyr_boot_and_secondary_cpus(SimpleNamespace(mgr=Manager(logs={"si_cl1": text})))


@pytest.mark.parametrize("records", [
    [(1, 0x10100), (2, 0x10100), (3, 0x10300)],
    [(1, 0x10400), (2, 0x10200), (3, 0x10300)],
    [(1, 0x10100), (2, 0x10200)],
    [(1, 0x10100), (2, 0x10200), (2, 0x10300)],
    [(1, 0x10100), (2, 0x10200), (3, 0x10300), (3, 0x10300)],
    [(1, 0x10200), (2, 0x10100), (3, 0x10300)],
])
def test_zephyr_boot_rejects_missing_duplicate_or_invalid_cpu_mapping(records):
    from scripts.run.qbox_validation.reuse_bsp import si1_boot_complete

    text = "Booting Zephyr OS build\n" + "\n".join(
        f"Secondary CPU core {cpu} (MPID:{mpid:#x}) is up" for cpu, mpid in records
    ) + "\nuart:~$"
    assert not si1_boot_complete(text)


@pytest.mark.parametrize("rc,output,passes", [
    (0, "__QBOX_BSP_CORE_PROBE_START__\nLinux\n", True),
    (1, "__QBOX_BSP_CORE_PROBE_START__\nLinux\n", False),
    (0, "Linux\n", False),
    (0, "__QBOX_BSP_CORE_PROBE_START__\nuname: Linux unavailable\n", False),
])
def test_linux_shell_is_preserved_as_separate_runtime_case(rc, output, passes):
    case = load_case("ap/devices/test_linux_shell.py")
    manager = Manager([(rc, output)])
    if passes:
        case.test_linux_uart_executes_guest_command(SimpleNamespace(mgr=manager))
    else:
        with pytest.raises(AssertionError):
            case.test_linux_uart_executes_guest_command(SimpleNamespace(mgr=manager))
    assert manager.commands == [("ap", "echo __QBOX_BSP_CORE_PROBE_START__; uname -s", 120)]


def test_zephyr_shell_is_preserved_as_separate_runtime_case():
    case = load_case("si_cl1/devices/test_kernel_shell.py")
    lines = CASES[3][3]
    manager = Manager([(0, "Zephyr version 4.1.0\n")], {"si_cl1": "\r\n".join(lines)})
    properties = []
    case.test_zephyr_kernel_version_command(SimpleNamespace(mgr=manager), lambda *v: properties.append(v))
    assert manager.commands[0][:2] == ("si_cl1", "kernel version")
    assert properties[0] == ("validation_profile", "si-cl1")
