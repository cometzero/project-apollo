# Configurable secondary AXI5 port

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Configurable-secondary-AXI5-port>

### Configurable secondary AXI5 port

The DMA-350 supports an extra complete AXI5 manager port when enabled through a configuration parameter. This allows easier connection to other parts of the system without the need of an interconnect. The secondary port also allows parallel read and write operations on both interfaces.

Both AXI5 manager ports use the same attributes, for example data width and issuing capability. Both ports are synchronous to the module clock while they have their own clock enable signals.

When using two AXI5 manager ports, the DMA-350 must be able to decide based on a given address whether it should be forwarded to AXI5\_M0 or AXI5\_M1 manager port. A SystemVerilog function is provided for this in a implementer-editable file. The delivered IP bundle contains an example file for this purpose.

For details, see the AXI5 manager port address mapping section of the Arm® CoreLink™ DMA-350 Controller Configuration and Integration Manual.
