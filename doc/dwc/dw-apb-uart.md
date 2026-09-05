# DW_apb_uart public-source guide

This note covers the classic Synopsys `DW_apb_uart` AMBA APB peripheral and
its Linux 8250 integration. It focuses on software-visible behavior rather
than RTL configuration and timing closure.

## Official documentation

| Item | Version | Link | Anonymous access on 2026-09-04 |
| --- | --- | --- | --- |
| Component catalog | 4.05a | [DW_apb_uart][catalog] | Available |
| Databook | 4.05a | [PDF][databook-pdf] / [HTML][databook-html] | SolvNet sign-in redirect |
| AMBA 2 User Guide | 2025.02a | [HTML][user-guide] | SolvNet sign-in redirect |

The public catalog describes an AMBA 2.0 APB UART with IrDA support and
16550-compatible registers. Synopsys [product material][product] and its
[technical article][article] also list optional 16750-style flow control,
configurable FIFOs and thresholds, DMA, asynchronous APB/baud clocks,
loopback, RS485, and APB3/APB4 support.

## 16550 compatibility and register spacing

The core follows the 16550 programming model, but a common APB integration
places logical UART registers on 32-bit boundaries. Linux represents this as
`reg-shift = <2>` and normally uses `reg-io-width = <4>`. Do not hard-code
that layout: both values are platform integration properties.

For a 32-bit-spaced instance, the common byte offsets are:

| Offset | Register | Purpose |
| ---: | --- | --- |
| `0x00` | `RBR` / `THR` / `DLL` | RX, TX, or divisor low byte selected by `LCR.DLAB` |
| `0x04` | `IER` / `DLH` | Interrupt enable or divisor high byte |
| `0x08` | `IIR` / `FCR` | Interrupt identification or FIFO control |
| `0x0c` | `LCR` | Word length, stop, parity, and divisor-latch access |
| `0x10` | `MCR` | Modem control and loopback |
| `0x14` | `LSR` | RX/TX and line-error state |
| `0x18` | `MSR` | Modem input and delta state |
| `0x1c` | `SCR` | Scratch register |
| `0x7c` | `USR` | DesignWare busy and FIFO status in the common layout |
| `0xa8` | `DMASA` | Optional DMA software acknowledgement |
| `0xac` | `TCR` | Optional RS485 transceiver control |
| `0xb0`-`0xb4` | `DE_EN`, `RE_EN` | Optional driver/receiver enables |
| `0xc0` | `DLF` | Optional fractional divisor |
| `0xc4`-`0xc8` | `RAR`, `TAR` | Optional 9-bit receive/transmit addresses |
| `0xcc` | `LCR_EXT` | Optional 9-bit/extended line control |
| `0xf4` | `CPR` | Encoded component parameters when implemented |
| `0xf8` | `UCV` | UART component version when implemented |

The base 16550 registers are deliberately summarized rather than duplicated.
Use the matching databook for access types, reset values, FIFO trigger
encodings, and optional shadow-register windows.

## Configuration discovery

When `CPR` is implemented and exposes encoded parameters, software can learn
the APB data width, automatic flow-control support, programmable THRE mode,
IrDA modes, extra feature registers, FIFO access/statistics, shadow registers,
extra DMA support, and FIFO depth. The Linux driver derives FIFO size as the
encoded FIFO mode multiplied by 16.

The Linux driver also probes whether `DLF` is writable and derives the number
of fractional-divisor bits from the implemented mask. An all-zero or absent
extended register set is valid for a reduced configuration.

## Safe initialization sequence

1. Enable the baud/reference clock and APB clock, then release reset.
2. Determine register width/spacing and read `UCV`/`CPR` if the integration
   exposes them.
3. Disable UART interrupts and clear or drain stale receive state.
4. Set `LCR.DLAB`, program the integer divisor (`DLL`/`DLH`) and optional
   fractional divisor (`DLF`), then restore the intended line format in `LCR`.
5. Configure and reset FIFOs through `FCR` when FIFOs are present.
6. Program modem/flow-control or RS485 settings only when the discovered
   configuration and board wiring support them.
7. Enable the required RX, TX-empty, line-status, and modem interrupts.

With the conventional 16-times sampling clock, the integer divisor is based
on `uartclk / (16 * baud)`. If `DLF` exists, the remainder is represented with
the discovered fractional width. Always calculate and report the achieved
baud and error; the requested baud alone is not sufficient.

## Runtime notes

- Read `IIR` until no interrupt is pending and service the highest-priority
  cause according to the 16550 model.
- Drain RX while `LSR` reports data ready and preserve parity, framing, break,
  and overrun status with the associated byte.
- Fill TX only while the FIFO can accept data; distinguish THR empty from
  transmitter completely empty when changing clocks or RS485 direction.
- Some DesignWare implementations reject an `LCR` write while the UART is
  busy. The Linux driver detects the busy condition through `USR` and retries
  the write through its DesignWare-specific accessors.
- RS485, 9-bit address matching, IrDA, fractional baud, DMA, and shadow
  registers are optional. Accessing an absent block may read zero, be ignored,
  or fault according to the surrounding bus integration.

## Linux device-tree contract

The generic compatible is `snps,dw-apb-uart`. The binding requires a register
range and a clock description through either `clock-frequency` or clock
providers. It supports `baudclk` and optional `apb_pclk`, interrupts, TX/RX
DMA, resets, power domains, register spacing/width, RS485 properties, and
modem-input overrides.

Set `snps,uart-16550-compatible` only when the configured RTL omits the
DesignWare busy functionality described by the binding. Incorrectly setting
it changes how the driver handles busy-detect behavior.

See the local [binding][binding], [platform driver][driver], and
[DesignWare 8250 library][library].

## Validation checklist

- Record `reg-shift`, `reg-io-width`, input clock, `UCV`, and `CPR`.
- Verify achieved baud error with a measured waveform or a trusted peer.
- Exercise all supported data bits, parity, stop bits, and FIFO thresholds.
- Validate RX overrun, parity/framing/break, TX-empty, and busy-detect paths.
- Test CTS/RTS and modem overrides against real board wiring.
- For RS485, capture DE/RE timing across the final stop bit and turnaround.
- For DMA, prove error propagation and residue handling as well as successful
  bulk transfer.

[catalog]: https://www.synopsys.com/dw/ipdir.php?c=DW_apb_uart
[databook-pdf]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_uart/4.05a/doc/DW_apb_uart_databook.pdf
[databook-html]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_uart/4.05a/doc/DW_apb_uart_databook/index.html
[user-guide]: https://www.synopsys.com/dw/doc.php/doc/amba/2025.02a/DW_iip_amba_user/index.html
[product]: https://www.synopsys.com/designware-ip/soc-infrastructure-ip/amba/amba-apb-advanced.html
[article]: https://www.synopsys.com/articles/understanding-peripherals.html
[binding]: ../../hsoc-stack/components/primary_compute/linux/Documentation/devicetree/bindings/serial/snps-dw-apb-uart.yaml
[driver]: ../../hsoc-stack/components/primary_compute/linux/drivers/tty/serial/8250/8250_dw.c
[library]: ../../hsoc-stack/components/primary_compute/linux/drivers/tty/serial/8250/8250_dwlib.c
