from scripts.test.probe_apollo_fvp_suspend import classify, guest_command


def test_command_echo_is_not_execution_evidence():
    assert classify(guest_command('deep', 10), True) == 'FAIL_OR_INCOMPLETE'


def test_missing_rtc_is_unsupported():
    assert classify('__AP_PM_UNSUPPORTED_RTC__\n', True) == 'UNSUPPORTED_RTC_WAKE'


def test_unadvertised_state_is_not_setup_failure():
    assert classify('__AP_PM_UNSUPPORTED_STATE__\n', True) == 'UNSUPPORTED_SUSPEND_STATE'
    command = guest_command('deep', 10)
    assert command.index('grep -qw deep') < command.index('echo +10')


def test_setup_failure_is_not_suspend_success():
    assert classify('__AP_PM_SETUP_FAILED__\n', True) == 'SETUP_FAILED'


def test_firmware_failure_is_classified():
    assert classify('', False, 'ASSERT: css_pm.c:260\n') == 'TF_A_ASSERT'
    assert classify('', False, 'ERROR: SCMI system power domain suspend return 0x4 unexpected') == 'SCMI_SUSPEND_FAILED'


def test_return_requires_kernel_markers_and_successful_runner():
    log = ('PM: suspend entry (deep)\nPM: suspend exit\n'
           '__AP_PM_RETURN_RC__=0\n__AP_PM_OS_CONTEXT_MATCH__\n__AP_PM_END__\n')
    assert classify(log, True) == 'OS_SUSPEND_RETURN_OBSERVED'
    assert classify(log, False) == 'FAIL_OR_INCOMPLETE'
    assert classify(log, False, diagnostic_shell=True) == 'OS_RETURN_OBSERVED_WITH_BOOT_FAILURE'
    assert classify(log.replace('PM: suspend exit', ''), True) == 'FAIL_OR_INCOMPLETE'
    assert classify(log.replace('RC__=0', 'RC__=1'), True) == 'FAIL_OR_INCOMPLETE'
    assert classify(log.replace('__AP_PM_OS_CONTEXT_MATCH__', ''), True) == 'FAIL_OR_INCOMPLETE'
    assert classify(log.replace('CONTEXT_MATCH', 'CONTEXT_MISMATCH'), True) == 'OS_CONTEXT_MISMATCH'


def test_context_setup_is_after_capability_check_and_before_suspend():
    command = guest_command('deep', 10)
    assert command.index('grep -qw deep') < command.index('mktemp -d /tmp')
    assert command.index('mount -t tmpfs') < command.index('dd if=/dev/urandom')
    assert command.index('pm_context_sum=') < command.index('echo mem >')
    assert command.index('echo mem >') < command.index('__AP_PM_OS_CONTEXT_MATCH__')


def test_generated_shell_syntax():
    import subprocess
    subprocess.run(['sh', '-n'], input=guest_command('deep', 10),
                   text=True, check=True)


def test_power_backend_evidence_is_not_context_resume():
    assert classify('', False, management_log=
                    '[PPU TEST] OFF timeout PWPR=00000000 PWSR=00000008') == 'AP_CORE_OFF_TIMEOUT'
    assert classify('', False, management_log=
                    '[SYS-POW TEST] AP SYS0 PPU OFF observed; arming timer') == 'AP_SYS0_OFF_OBSERVED_NO_OS_RESUME'


def test_retention_failure_and_match_are_not_os_resume():
    assert classify('', False, management_log=
                    '[SYS-POW TEST] SRAM retention failed; CPU release blocked: -2') == 'AP_SRAM_RETENTION_FAILED'
    assert classify('', False, management_log=
                    '[AP SRAM TEST] retained 2 MiB fingerprint match') == 'FAIL_OR_INCOMPLETE'


def test_systop_on_is_not_domain_off_or_os_return():
    log = '[SYS-POW TEST] AP cores/clusters OFF; SYSTOP remains ON; arming timer (logical SLEEP0)'
    assert classify('', False, management_log=log) == 'AP_COMPUTE_OFF_SYSTOP_ON_NO_OS_RESUME'
