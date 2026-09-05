from __future__ import annotations

from scripts.run import run_qbox_apollo_fvp_full as full_runner

runtime = full_runner.runtime_engine


def complete_console() -> str:
    lines = [runtime.DWC_PROBE_START_MARKER]
    lines.extend(
        "__QBOX_DWC_I2C|bus="
        f"{bus}|addr=0x50|driver_rc=0|write_rc=0|read_rc=0|cmp_rc=0"
        for bus in range(6)
    )
    lines.extend(
        (
            "__QBOX_DWC_SPI|module_rc=0|bound=4|timeout_margin_ms=30000|restore_rc=0|unload_rc=0|fresh_load=1",
            "__QBOX_DWC_UART|direction=0-to-1|stty_tx_rc=0|stty_rx_rc=0|write_rc=0|read_rc=0|cmp_rc=0",
            "__QBOX_DWC_UART|direction=1-to-0|stty_tx_rc=0|stty_rx_rc=0|write_rc=0|read_rc=0|cmp_rc=0",
            "__QBOX_DWC_UART|direction=2-to-3|stty_tx_rc=0|stty_rx_rc=0|write_rc=0|read_rc=0|cmp_rc=0",
            "__QBOX_DWC_UART|direction=3-to-2|stty_tx_rc=0|stty_rx_rc=0|write_rc=0|read_rc=0|cmp_rc=0",
            runtime.DWC_PROBE_DONE_MARKER,
        )
    )
    return "\n".join(lines)


def test_dwc_probe_commands_use_bounded_busybox_compatible_contract() -> None:
    # Given: the guest command sequence requested after a root-shell login.
    commands = runtime.dwc_peripheral_probe_commands()
    combined = "\n".join(commands)
    # The deployed BusyBox editor has a 1024-byte input buffer.
    assert all(len(command.encode()) < 1023 for command in commands)

    # Then: all required devices are covered without a dependency on i2c-tools.
    for bus in range(6):
        assert f"/sys/bus/i2c/devices/{bus}-0050" in combined
    assert 'readlink "$dev/driver"' in combined
    assert 'readlink "$p/../driver"' not in combined
    assert 'cat "$tx" > "$p"' in combined
    assert "conv=notrunc" not in combined
    assert "modprobe -r spi-loopback-test" in combined
    assert "if [ ! -d /sys/module/spi_loopback_test ]" in combined
    assert "modprobe spi-loopback-test loopback=1 loop_req=1 delay_ms=0" in combined
    assert "/sys/module/spi/parameters/transfer_timeout_margin_ms" in combined
    assert 'echo "$dwc_saved_margin" > "$dwc_timeout_path"' in combined
    assert "/sys/bus/spi/drivers/spi-loopback-test/spi*" in combined
    assert "timeout" not in combined.split()
    assert "while kill -0" in combined
    assert "r=124" in combined
    for direction in ("0-to-1", "1-to-0", "2-to-3", "3-to-2"):
        assert f"dwc_uart_transfer /dev/ttyS{direction[0]} /dev/ttyS{direction[-1]} {direction}" in combined


def test_dwc_probe_evaluator_preserves_return_codes_and_rejects_failure() -> None:
    # Given: complete guest evidence, except one EEPROM compare failure.
    console = complete_console().replace(
        "bus=5|addr=0x50|driver_rc=0|write_rc=0|read_rc=0|cmp_rc=0",
        "bus=5|addr=0x50|driver_rc=0|write_rc=0|read_rc=0|cmp_rc=1",
    )

    # When: the artifact evaluator consumes the primary UART log.
    result = runtime.evaluate_dwc_peripheral_probe(console, requested=True)

    # Then: request state and exact command return code survive as a failure.
    assert result["requested"] is True
    assert result["complete"] is True
    assert result["passed"] is False
    assert result["i2c"]["devices"]["5"]["cmp_rc"] == 1


def test_dwc_probe_evaluator_accepts_complete_guest_evidence() -> None:
    result = runtime.evaluate_dwc_peripheral_probe(complete_console(), requested=True)

    assert result["passed"] is True
    assert result["spi"]["bound"] == 4
    assert result["spi"]["timeout_margin_ms"] == 30000
    assert result["spi"]["restore_rc"] == 0
    assert result["uart"]["directions"]["2-to-3"]["cmp_rc"] == 0


def test_dwc_probe_rejects_failed_timeout_restoration() -> None:
    console = complete_console().replace("restore_rc=0", "restore_rc=1")
    result = runtime.evaluate_dwc_peripheral_probe(console, requested=True)

    assert result["spi"]["passed"] is False
    assert result["passed"] is False


def test_dwc_probe_rejects_stale_module_bindings() -> None:
    console = complete_console().replace(
        "unload_rc=0|fresh_load=1", "unload_rc=1|fresh_load=0"
    )
    result = runtime.evaluate_dwc_peripheral_probe(console, requested=True)

    assert result["spi"]["module_rc"] == 0
    assert result["spi"]["bound"] == 4
    assert result["spi"]["passed"] is False
    assert result["passed"] is False


def test_dwc_probe_enables_post_login_and_forwards_to_runtime_child() -> None:
    # Given: the public full-system runner receives only the DWC selection.
    args = full_runner.parse_args(["--dwc-peripheral-probe"])
    artifacts = full_runner.resolved_artifacts(args)

    # When: it builds its private runtime child invocation.
    command = full_runner.child_command(args, artifacts)

    # Then: the probe selects the normal post-login transport and is forwarded.
    assert args.post_login_probe is True
    assert "--post-login-probe" in command
    assert "--dwc-peripheral-probe" in command
