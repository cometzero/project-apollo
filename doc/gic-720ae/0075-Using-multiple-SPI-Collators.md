# Using multiple SPI Collators

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/SPI-Collator/Using-multiple-SPI-Collators>

### Using multiple SPI Collators

If a GIC configuration uses multiple SPI Collators, then the SPI\_BASE value must be set so that the SPI wires do not overlap.

The SPI\_BASE value controls the base address of an SPI Collator, and it is set by using either an `SPI_BASE` build-time option or an spi\_base signal. The choice of whether to use build-time options or signals, to set the base address of all SPI Collators on the chip, is decided during configuration.

For example, if the chip uses the `SPI_BASE` build-time option to set the base addresses of its 3 SPI Collators, then the `SPI_BASE` options could be set to:

- 1 SPI Collator with 64 wires - `SPI_BASE` 0
- 1 SPI Collator with 32 wires - `SPI_BASE` 64
- 1 SPI Collator with 128 wires - `SPI_BASE` 96

SPI Collators do not have to support a multiple of 32 wires.

If the setting of SPI\_BASE causes SPI Collators to overlap, then interrupt corruption might occur, even when the overlapped INTIDs are tied to 0 on one of the SPI Collators.
