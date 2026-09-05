# Apollo QVP DesignWare APB integration

The QVP uses reusable SystemC/TLM models in QBox core, instantiated by
`qbox-platform/platforms/apollo/hw-block/ros.lua`. Linux uses its existing
DesignWare drivers through `arch/arm64/boot/dts/arm/apollo-qvp.dts`.

## AP allocation

Each instance occupies 64 KiB. The allocation uses the reserved RoS area
within AP Memory Expansion; see the
[AP programmer's model](../arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md)
and [FVP RoS map](../arm_zena_css_dev_guide/08-fixed-virtual-platform.md).
These are QVP additions, not an assertion that FVP provides these devices.

| Devices | Bases, 64 KiB stride | GIC SPI selectors | INTIDs | Connection |
| --- | --- | --- | --- | --- |
| I2C0–5 | `0x30100000`–`0x30150000` | 320–325 | 352–357 | One 256-byte 24C02 at address `0x50` per bus |
| SSI0–3 | `0x30160000`–`0x30190000` | 326–329 | 358–361 | PSSI shift-register loopback (`SPI_LOOP`) |
| UART0–3 | `0x301a0000`–`0x301d0000` | 330–333 | 362–365 | UART0 ↔ UART1, UART2 ↔ UART3 |

All interrupts are level-high. QBox IRQ outputs use
`InitiatorSignalSocket<bool>` to bind to the QEMU GIC signal sockets.
The existing PL011 remains the console.

`nexios-apollo-qboxboot.inc` selects `KERNEL_DEVICETREE:apollo-qvp` for
both images so their UKIs contain the Linux `apollo-qvp.dtb`. Without this
image-context setting, U-Boot passes the firmware's TF-A HW_CONFIG tree,
which does not contain the DWC devices.

## Build and guest test

```bash
./yocto_build.sh --bsp
./run_qbox_yocto.sh --bsp --headless --exit-after-pass \
  --dwc-peripheral-probe --timeout 3600 \
  --copy-disks --no-persistent-rse-state --record-initial-state \
  --out-dir build/qbox-apollo-qvp/dwc-runtime
```

The BSP includes the AT24 and DesignWare I2C, SPI MMIO, and 8250 DW drivers,
plus the `spi-loopback-test` kernel module. The opt-in probe enables the
canonical post-login transport and records device results under
`post_login_probe.dwc_peripheral_probe` in `result.json`.

Acceptance requires all six AT24 EEPROM write/read comparisons, successful
kernel loopback tests on all four SPI devices, and byte-for-byte comparison
in each of the four UART transfer directions. A successful build or driver
enumeration alone is insufficient.

The probe temporarily sets
`/sys/module/spi/parameters/transfer_timeout_margin_ms` to 30000 ms for the
full kernel loopback suite and restores its previous value afterward. The
SPI core default remains 200 ms. The result records the effective margin
and requires successful restoration. This extends the guest transfer
deadline; the launcher's `--timeout` independently bounds the entire run.

## Scope

I2C implements bounded 7-bit controller and EEPROM transactions, including
repeated starts and page writes. SSI implements classic PSSI internal
loopback. UART implements 16550/DW registers, FIFO behavior, baud-timed
transmit, and receive timeout. DMA, I2C arbitration/target mode, external SSI
targets, advanced SSI protocols, UART modem signaling, and bit-level
electrical timing remain unsupported.

## Storage recovery evidence

On 2026-09-05, a zero-byte CPIO manifest from the preceding NVMe failure
caused `do_image_complete` to raise `JSONDecodeError`. Rootfs, image metadata,
and deployment ownership state were also damaged. Regenerating the image
from its packages and quarantining only conflicting orphaned outputs restored
the BSP build. Generated logs and recoverable backups are under
`build/qbox-apollo-qvp/dwc-recovery-20260905/`.

The recovery also exposed two integration gaps: DWC IRQ outputs needed QBox
signal sockets, and the UKI needed an explicit Linux DTB. Both are corrected.
At the default 10 ms quantum, live EEPROM tests pass on all six buses and
UART transfers pass in both directions on both pairs. The full Linux SPI
loopback suite still encounters long-transfer timeouts under the freerunning
configuration; this is not covered by the standalone 4 KiB SSI test passing
at 1 MHz. Consult the run-local results before treating SPI as qualified.

## Long-timeout result, 2026-09-05

`runtime-long-timeout/` completed with the default 10 ms quantum and a
30000 ms SPI timeout margin. All four controllers passed the first basic
TX/RX test's 65536- and 65537-byte alignment combinations, then timed out
at 131071 bytes, including the kernel test's retry. The remaining test
families were not reached because the driver stops on failure. The full
SPI qualification is therefore **FAIL**, not a full-length/protocol pass.

All six EEPROM checks and all four UART directions passed. All baseline
driver checks, including SMMUv3, passed. The core timeout setting was read
back as 200 ms after the test. The BSP build passed all 5541 tasks; final
focused Python/DTS tests passed 71 tests and DWC CTest passed 3/3 binaries.

The generated `runtime-long-timeout/result.json`, `timeout-restoration.txt`,
and `full-coverage-audit.json` retain the failure and cleanup evidence below
the recovery directory. The overall runtime/coverage result remains failed
because SPI qualification did not pass.
