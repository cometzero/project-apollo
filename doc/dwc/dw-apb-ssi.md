# DW_apb_ssi public-source guide

This note covers the classic Synopsys `DW_apb_ssi` AMBA APB synchronous serial
interface, commonly used as an SPI controller. SSI is the IP block name; SPI
is one of its supported serial protocols.

## Official documentation

| Item | Version | Link | Anonymous access on 2026-09-04 |
| --- | --- | --- | --- |
| Component catalog | 4.05a | [DW_apb_ssi][catalog] | Available |
| Databook | 4.05a | [PDF][databook-pdf] / [HTML][databook-html] | SolvNet sign-in redirect |
| AMBA 2 User Guide | 2025.02a | [HTML][user-guide] | SolvNet sign-in redirect |

Synopsys separately lists the high-performance `DWC_ssi` product at version
3.00a with its own [catalog][dwc-catalog], [databook][dwc-databook],
[reference manual][dwc-reference], and [user guide][dwc-user]. Those manuals
also require SolvNet authentication. Select documentation by the actual RTL
component and version, not by the generic word “SPI.”

The public Synopsys [product page][product] and [technical article][article]
list Motorola SPI, TI SSP, and National Semiconductor Microwire modes. They
also describe standard/dual/quad/octal SPI, RX sample delay, XIP, DDR,
read-data strobe, data mask, and DMA features. These advanced modes are
version- and configuration-dependent and are not described by the small
generic register subset below.

## Software-visible model

The classic block combines:

- an APB programming interface;
- configurable TX and RX FIFOs;
- one or more native chip-select outputs;
- a serial engine with selectable frame format, clock polarity/phase, data
  frame size, and transfer mode;
- optional interrupt and DMA request paths.

Linux uses the same basic register offsets for classic DWC APB SSI and newer
DWC SSI variants, but it applies different `CTRLR0` field layouts. A virtual
platform must model the selected variant explicitly.

## Core register map

| Offset | Register | Purpose |
| ---: | --- | --- |
| `0x00` | `CTRLR0` | Frame size/format, CPOL/CPHA, transfer mode, loopback |
| `0x04` | `CTRLR1` | Number of receive frames for receive/EEPROM-read modes |
| `0x08` | `SSIENR` | SSI enable |
| `0x0c` | `MWCR` | Microwire control |
| `0x10` | `SER` | Native target/chip-select enable mask |
| `0x14` | `BAUDR` | Serial clock divider |
| `0x18`-`0x1c` | `TXFTLR`, `RXFTLR` | FIFO interrupt thresholds |
| `0x20`-`0x24` | `TXFLR`, `RXFLR` | FIFO fill levels |
| `0x28` | `SR` | Busy, FIFO, transmit-error, and collision state |
| `0x2c` | `IMR` | Interrupt mask |
| `0x30` | `ISR` | Masked interrupt state |
| `0x34` | `RISR` | Raw interrupt state |
| `0x38`-`0x48` | `*ICR` | Source-specific and combined interrupt clear reads |
| `0x4c` | `DMACR` | TX/RX DMA enable |
| `0x50`-`0x54` | `DMATDLR`, `DMARDLR` | DMA request thresholds |
| `0x58` | `IDR` | Identification value when implemented |
| `0x5c` | `VERSION` | Component version |
| `0x60` and above | `DR[]` | Data registers/FIFO access window |
| `0xf0` | `RX_SAMPLE_DLY` | Optional RX sampling delay |

Some platform variants use `0xf4` for a vendor-specific chip-select override.
Do not treat it as part of the portable base contract.

For classic APB SSI, the common `CTRLR0` choices are Motorola SPI, TI SSP, or
Microwire frame format; SPI CPOL/CPHA; transmit-and-receive, transmit-only,
receive-only, or EEPROM-read transfer mode; and a synthesized data-frame-size
range.

## Safe initialization and transfer

1. Enable the reference/APB clocks and release reset.
2. Write `SSIENR=0` before changing the main transfer configuration.
3. Read the ID/version and determine FIFO depth and supported frame sizes by
   integration data or a non-destructive probe supported by the driver.
4. Program `CTRLR0`, optional `CTRLR1`, an even non-zero baud divisor, and FIFO
   thresholds.
5. Mask or configure interrupts and prepare DMA if selected.
6. Select the intended native chip select in `SER`.
7. Enable the core, then keep the TX FIFO supplied and drain the RX FIFO until
   all frames complete and `SR.BUSY` clears.
8. Disable the core before reprogramming the next incompatible transfer.

The common status bits report busy, TX-not-full, TX-empty, RX-not-empty,
RX-full, TX error, and data collision. The common interrupt set covers TX
empty/overflow, RX underflow/overflow/full, and multi-controller contention.

## Native chip-select caveat

The upstream Linux driver documents an important behavior of unmodified
classic DW APB SSI integrations: native chip select can be asserted by an
active transmission and automatically deasserted when the TX FIFO becomes
empty. Scheduler or interrupt latency can therefore split a transaction if
software fails to keep the FIFO fed.

For a transaction that must hold CS across command, address, dummy, and data
phases, use a proven SPI-memory path, DMA, or a GPIO/external CS mechanism as
appropriate for the platform. Validate the waveform; software completion
alone does not prove continuous CS.

## Linux device-tree contract

The generic compatible is `snps,dw-apb-ssi`. The binding requires a register
range, clocks, SPI child-address cells, and normally one interrupt. It supports
one or two clocks (`ssi_clk`, `pclk`), reset, 16- or 32-bit register I/O,
one to four chip selects, TX/RX DMA, GPIO chip selects, and an optional RX
sample delay.

`snps,dwc-ssi-1.01a` is a distinct compatible accepted by the same binding.
Vendor compatibles and quirks should precede the generic fallback where the
binding specifies that ordering.

See the local [binding][binding], [register definitions][core],
[core driver][driver], and [MMIO integration][mmio].

## Validation checklist

- Record the RTL component name/version and active Linux compatible.
- Confirm register width, clock rate, FIFO depth, maximum frame size, and
  number of chip selects.
- Sweep SPI modes 0 through 3 at low speed before increasing the clock.
- Verify TX-only, RX-only, and full-duplex FIFO accounting.
- Force FIFO underflow/overflow and confirm interrupt clear behavior.
- Capture CS, SCLK, and data-lane waveforms for multi-part and DMA transfers.
- Treat dual/quad/octal, DDR, XIP, and sample-delay support as unproven until
  both parameter discovery and real traffic confirm them.

[catalog]: https://www.synopsys.com/dw/ipdir.php?c=DW_apb_ssi
[databook-pdf]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_ssi/4.05a/doc/DW_apb_ssi_databook.pdf
[databook-html]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_ssi/4.05a/doc/DW_apb_ssi_databook/index.html
[user-guide]: https://www.synopsys.com/dw/doc.php/doc/amba/2025.02a/DW_iip_amba_user/index.html
[dwc-catalog]: https://www.synopsys.com/dw/ipdir.php?c=dwc_ssi
[dwc-databook]: https://www.synopsys.com/dw/doc.php/iip/DWC_ssi/3.00a/doc/DWC_ssi_databook.pdf
[dwc-reference]: https://www.synopsys.com/dw/doc.php/iip/DWC_ssi/3.00a/doc/DWC_ssi_reference.pdf
[dwc-user]: https://www.synopsys.com/dw/doc.php/iip/DWC_ssi/3.00a/doc/DWC_ssi_user.pdf
[product]: https://www.synopsys.com/designware-ip/soc-infrastructure-ip/amba/amba-apb-advanced.html
[article]: https://www.synopsys.com/articles/understanding-peripherals.html
[binding]: ../../hsoc-stack/components/primary_compute/linux/Documentation/devicetree/bindings/spi/snps,dw-apb-ssi.yaml
[core]: ../../hsoc-stack/components/primary_compute/linux/drivers/spi/spi-dw.h
[driver]: ../../hsoc-stack/components/primary_compute/linux/drivers/spi/spi-dw-core.c
[mmio]: ../../hsoc-stack/components/primary_compute/linux/drivers/spi/spi-dw-mmio.c
