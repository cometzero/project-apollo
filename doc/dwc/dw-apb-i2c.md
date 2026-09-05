# DW_apb_i2c public-source guide

This note covers the classic Synopsys `DW_apb_i2c` AMBA APB peripheral. It is
intended for driver, device-tree, and virtual-platform work. It does not
replace the licensed RTL integration documentation.

## Official documentation

| Item | Version | Link | Anonymous access on 2026-09-04 |
| --- | --- | --- | --- |
| Component catalog | 2.05a | [DW_apb_i2c][catalog] | Available |
| Databook | 2.05a | [PDF][databook-pdf] / [HTML][databook-html] | SolvNet sign-in redirect |
| AMBA 2 User Guide | 2025.02a | [HTML][user-guide] | SolvNet sign-in redirect |

The public catalog describes the component as an AMBA 2.0 APB I2C device.
The public Synopsys [product page][product] and [technical article][article]
advertise standard, fast, and high-speed I2C modes, 7-bit and 10-bit
addressing, configurable FIFOs, optional DMA, SMBus/PMBus functions, bus
clear, clock stretching, and optional multi-target support. Treat each item
as configuration-dependent.

## Software-visible model

The core has an APB register interface on the system side and open-drain SCL
and SDA behavior on the bus side. A configured instance can act as an I2C
controller, an I2C target, or expose only a subset of the advertised modes.

Software normally interacts with four functional groups:

1. Core and address configuration through `IC_CON`, `IC_TAR`, and `IC_SAR`.
2. Bus timing through the standard/fast/high-speed SCL count registers and
   the optional SDA hold register.
3. Transfer FIFOs through `IC_DATA_CMD`, FIFO thresholds, and FIFO levels.
4. Completion and fault handling through masked/raw interrupt state and
   `IC_TX_ABRT_SOURCE`.

## Configuration discovery

Do not infer the synthesized feature set from the IP family name alone.

| Offset | Register | Typical software use |
| ---: | --- | --- |
| `0xf4` | `IC_COMP_PARAM_1` | Discover encoded FIFO depths and capabilities |
| `0xf8` | `IC_COMP_VERSION` | Apply version-dependent behavior |
| `0xfc` | `IC_COMP_TYPE` | Validate a DesignWare I2C block; Linux expects `0x44570140` |

The Linux driver also treats SDA hold programming as version-dependent and
checks for an implementation at least as new as the `1.11*` family before
using the standard register.

## Core register map

This is the software subset used by the in-tree Linux driver. Optional or
newer SMBus/PMBus registers are intentionally omitted because their presence
depends on the licensed configuration.

| Offset | Register group | Purpose |
| ---: | --- | --- |
| `0x00` | `IC_CON` | Controller/target mode, speed, addressing, restart, bus-clear policy |
| `0x04` | `IC_TAR` | Current controller-mode target address |
| `0x08` | `IC_SAR` | Target-mode local address |
| `0x10` | `IC_DATA_CMD` | TX data, RX read commands, and received data |
| `0x14`-`0x18` | `IC_SS_SCL_*CNT` | Standard-speed SCL high/low counts |
| `0x1c`-`0x20` | `IC_FS_SCL_*CNT` | Fast-speed SCL high/low counts |
| `0x24`-`0x28` | `IC_HS_SCL_*CNT` | High-speed SCL high/low counts |
| `0x2c` | `IC_INTR_STAT` | Masked interrupt state |
| `0x30` | `IC_INTR_MASK` | Interrupt enable mask |
| `0x34` | `IC_RAW_INTR_STAT` | Raw interrupt state |
| `0x38`-`0x3c` | `IC_RX_TL`, `IC_TX_TL` | FIFO interrupt thresholds |
| `0x40`-`0x68` | `IC_CLR_*` | Combined and source-specific interrupt clear reads |
| `0x6c` | `IC_ENABLE` | Core enable and optional transfer abort request |
| `0x70` | `IC_STATUS` | Activity and FIFO state |
| `0x74`-`0x78` | `IC_TXFLR`, `IC_RXFLR` | Current FIFO fill levels |
| `0x7c` | `IC_SDA_HOLD` | TX/RX SDA hold timing when implemented |
| `0x80` | `IC_TX_ABRT_SOURCE` | Detailed controller-transfer abort cause |
| `0x9c` | `IC_ENABLE_STATUS` | Synchronized enable state |

For `IC_DATA_CMD`, the common programming model uses bits `[7:0]` for data,
bit 8 to enqueue a read, bit 9 to request STOP, and bit 10 to request RESTART.
The exact availability and semantics must be checked against the matching
databook revision.

## Safe initialization sequence

1. Enable the APB and reference clocks and release reset.
2. Disable the core with `IC_ENABLE` and wait for `IC_ENABLE_STATUS` to
   acknowledge the disabled state.
3. Read the component type, version, and parameter registers.
4. Program SCL high/low counts for the selected bus rate and, when supported,
   program SDA hold time.
5. Program FIFO thresholds, target/local addresses, and `IC_CON`.
6. Mask interrupts and clear stale causes with the documented clear reads.
7. Enable the core and confirm the synchronized enable state.

Configuration registers should not be changed while the block is enabled
unless the matching databook explicitly permits the operation.

## Controller transfer outline

- Program one target address in `IC_TAR` for the transaction.
- For writes, enqueue bytes in `IC_DATA_CMD` while TX space is available.
- For reads, enqueue one read command per expected byte and drain the RX FIFO
  before it can overflow.
- Set RESTART on the first command of a repeated-start message when required.
- Set STOP on the final command, then wait for STOP detection or an abort.
- On `TX_ABRT`, save `IC_TX_ABRT_SOURCE` before clearing the interrupt; the
  source distinguishes address/data NACK, disabled-controller requests,
  arbitration loss, and target-side conflicts.

The number of outstanding reads must never exceed the synthesized RX FIFO
depth. Long messages therefore need interrupt, polling, or DMA flow control.

## Interrupts and recovery

The common interrupt set includes RX underflow/overflow/full, TX overflow or
empty, target read request, TX abort, activity, STOP/START detection, general
call, restart detection, and controller-on-hold. Some clear registers use
read-to-clear semantics, so a diagnostic path should capture raw and abort
state before clearing it.

After an abort or timeout:

1. Stop feeding new commands and capture the raw status and abort source.
2. Disable the controller and wait for the disable acknowledgement.
3. Clear pending interrupt state and software FIFO bookkeeping.
4. If SDA or SCL remains stuck, use a synthesized bus-clear facility or a
   board-level recovery procedure; do not assume the feature exists.
5. Restore configuration and re-enable the block.

## Linux device-tree contract

The generic compatible is `snps,designware-i2c`. The binding requires a
register range and interrupt. It supports a reference clock plus an optional
APB clock, reset, TX/RX DMA channels, bus frequency, signal fall times, SDA
hold time, and high-speed bus-capacitance/clock-optimization properties.

The generic binding accepts 100 kHz, 400 kHz, 1 MHz, and 3.4 MHz. A board must
still satisfy its electrical timing and pull-up requirements; a requested
frequency is not evidence that the physical bus meets the I2C specification.

See the local [binding][binding], [common driver definitions][core],
[controller driver][master], and [target driver][target].

## Validation checklist

- Read and record component type, version, and parameter values.
- Confirm APB register width and endianness before relying on bulk access.
- Measure the actual SCL frequency and high/low periods.
- Exercise address NACK, data NACK, arbitration loss, STOP, and timeout paths.
- Verify FIFO thresholds and interrupt masking under long bidirectional
  transfers.
- If DMA is enabled, prove both DMA completion and controller STOP/error
  handling; either one alone is insufficient.

[catalog]: https://www.synopsys.com/dw/ipdir.php?c=DW_apb_i2c
[databook-pdf]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_i2c/2.05a/doc/DW_apb_i2c_databook.pdf
[databook-html]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_i2c/2.05a/doc/DW_apb_i2c_databook/index.html
[user-guide]: https://www.synopsys.com/dw/doc.php/doc/amba/2025.02a/DW_iip_amba_user/index.html
[product]: https://www.synopsys.com/designware-ip/soc-infrastructure-ip/amba/amba-apb-advanced.html
[article]: https://www.synopsys.com/articles/understanding-peripherals.html
[binding]: ../../hsoc-stack/components/primary_compute/linux/Documentation/devicetree/bindings/i2c/snps,designware-i2c.yaml
[core]: ../../hsoc-stack/components/primary_compute/linux/drivers/i2c/busses/i2c-designware-core.h
[master]: ../../hsoc-stack/components/primary_compute/linux/drivers/i2c/busses/i2c-designware-master.c
[target]: ../../hsoc-stack/components/primary_compute/linux/drivers/i2c/busses/i2c-designware-slave.c
