# Issuing capabilities

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Issuing-capabilities>

### Issuing capabilities

Read issuing capability is limited by the FIFO depth of every channel separately to 1, 2, 4, 8, 16, 32, 64. The channels issue reads when they have enough space to store the complete read response.

Write issuing capability depends on the transfer size and the data stored in the internal FIFO of the channel. A write is issued when the FIFO contains the full burst with all its beats.

The number of transfers issued depends on the command type and the address alignment.

The maximum issuing capability is limited by the DMA unit to avoid overloading the AXI infrastructure with too many outstanding transfers. The software can control the number of transfers outstanding on the bus. This enables debug and bus utilization shaping if the bus is still overloaded.
