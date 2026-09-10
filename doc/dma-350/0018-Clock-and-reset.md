# Clock and reset

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Clock-and-reset>

### Clock and reset

The DMA-350 is intended to be placed in a single clock and reset domain.

The APB4 configuration interface and the AXI5 manager interfaces (M0 and M1) use a clock enable signal to support these interfaces to run on a divided frequency. The APB configuration interface uses the pclken signal, the M0 interface uses the aclken\_m0 signal, and the M1 interface uses the aclken\_m1 signal.

> ### Note
>
> The optional AXI4-Stream manager and subordinate interfaces have no clock enable signal, they use the module clock directly.

The DMA-350 uses a single, active-LOW reset, resetn. This reset must be deasserted synchronously with the clk clock signal, but it can be asserted asynchronously.

There are no special powerup requirements defined for DMA-350.
