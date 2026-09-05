# Synopsys DesignWare APB peripheral references

Last verified: 2026-09-04

This directory is a public-source development reference for the classic
Synopsys DesignWare AMBA APB I2C, SSI/SPI, and UART peripherals. It records
the official document identifiers and provides independently written
programming notes derived from public Synopsys material and the Linux
drivers in this workspace.

## Document index

[Apollo QVP integration and guest tests](apollo-qvp-integration.md) describes
the instantiated models, AP allocation, build command, and validation scope.

| Peripheral | Public catalog version | Official databook | User guide | Local reference |
| --- | --- | --- | --- | --- |
| `DW_apb_i2c` | 2.05a | [PDF][i2c-db-pdf] / [HTML][i2c-db-html] | [AMBA 2 User Guide][amba-user] | [dw-apb-i2c.md](dw-apb-i2c.md) |
| `DW_apb_ssi` | 4.05a | [PDF][ssi-db-pdf] / [HTML][ssi-db-html] | [AMBA 2 User Guide][amba-user] | [dw-apb-ssi.md](dw-apb-ssi.md) |
| `DW_apb_uart` | 4.05a | [PDF][uart-db-pdf] / [HTML][uart-db-html] | [AMBA 2 User Guide][amba-user] | [dw-apb-uart.md](dw-apb-uart.md) |

The common user guide is listed by Synopsys as *Synopsys IP Synthesizable
Components for AMBA 2 User Guide*, version 2025.02a.

## Access status

The component catalog pages are public. The official databook and user-guide
URLs redirected an anonymous request to the Synopsys SolvNet/Okta sign-in
page when checked on 2026-09-04. A licensed Synopsys account may therefore be
required to read or download the full manuals.

This repository does not copy unofficial PDF mirrors or reproduce the
proprietary manuals. The local Markdown files are concise engineering guides,
not replacements for the licensed databooks. Use the matching licensed
databook for RTL configuration parameters, signal timing, reset values,
integration constraints, and verification requirements.

## Scope and version cautions

- `DW_apb_ssi` is the classic AMBA APB component represented by the Linux
  compatible `snps,dw-apb-ssi`. Synopsys also publishes the newer `DWC_ssi`
  product; do not assume that all control fields are interchangeable.
- Synopsys also lists newer advanced `dwc_i2c` and `dwc_uart` products. They
  are outside the scope of these notes.
- DesignWare IP is configurable. FIFO depth, DMA, target/controller modes,
  protocol extensions, and some registers can be synthesized in or out.
  Software should inspect identification and parameter registers where the
  integration exposes them.
- The local Linux reference was `v6.18.5-160-gdd2017a8dd0d` at the time of
  writing. Platform-specific integrations may add quirks or move registers.

## Public supporting sources

- [Synopsys APB Advanced Peripherals][synopsys-product] lists the supported
  I2C, UART, and SSI feature families.
- [Synopsys advanced-peripherals article][synopsys-article] explains UART
  fractional baud/RS485, SSI multi-lane SPI, and I2C SMBus/PMBus use cases.
- The in-tree Linux bindings and drivers provide an open-source software
  contract for deployed implementations:
  - [I2C binding][linux-i2c-binding] and [driver registers][linux-i2c-core]
  - [SSI binding][linux-ssi-binding] and [driver registers][linux-ssi-core]
  - [UART binding][linux-uart-binding] and [DesignWare 8250 support][linux-uart-core]

[i2c-db-pdf]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_i2c/2.05a/doc/DW_apb_i2c_databook.pdf
[i2c-db-html]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_i2c/2.05a/doc/DW_apb_i2c_databook/index.html
[ssi-db-pdf]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_ssi/4.05a/doc/DW_apb_ssi_databook.pdf
[ssi-db-html]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_ssi/4.05a/doc/DW_apb_ssi_databook/index.html
[uart-db-pdf]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_uart/4.05a/doc/DW_apb_uart_databook.pdf
[uart-db-html]: https://www.synopsys.com/dw/doc.php/iip/DW_apb_uart/4.05a/doc/DW_apb_uart_databook/index.html
[amba-user]: https://www.synopsys.com/dw/doc.php/doc/amba/2025.02a/DW_iip_amba_user/index.html
[synopsys-product]: https://www.synopsys.com/designware-ip/soc-infrastructure-ip/amba/amba-apb-advanced.html
[synopsys-article]: https://www.synopsys.com/articles/understanding-peripherals.html
[linux-i2c-binding]: ../../hsoc-stack/components/primary_compute/linux/Documentation/devicetree/bindings/i2c/snps,designware-i2c.yaml
[linux-i2c-core]: ../../hsoc-stack/components/primary_compute/linux/drivers/i2c/busses/i2c-designware-core.h
[linux-ssi-binding]: ../../hsoc-stack/components/primary_compute/linux/Documentation/devicetree/bindings/spi/snps,dw-apb-ssi.yaml
[linux-ssi-core]: ../../hsoc-stack/components/primary_compute/linux/drivers/spi/spi-dw.h
[linux-uart-binding]: ../../hsoc-stack/components/primary_compute/linux/Documentation/devicetree/bindings/serial/snps-dw-apb-uart.yaml
[linux-uart-core]: ../../hsoc-stack/components/primary_compute/linux/drivers/tty/serial/8250/8250_dwlib.c
