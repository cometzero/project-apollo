from scripts.run.runfvp_log_boot import check_console, latest_root_prompt_end


def test_recovery_prompt_requires_explicit_opt_in():
    log = 'NEXIOS_BSP_INITRAMFS_FAILED\nnexios-bsp-failed# '
    assert latest_root_prompt_end(log) == 0
    assert latest_root_prompt_end(log, True) == len(log)
    assert not check_console('terminal_ns_uart0', log)['passed']


def test_embedded_or_echoed_prompt_is_not_ready():
    assert latest_root_prompt_end('echo nexios-bsp-failed# ', True) == 0
