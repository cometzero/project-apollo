# AXI bandwidth utilization

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/AXI-bandwidth-utilization>

### AXI bandwidth utilization

This section provides a definition of terms used and optimization requirements.

### Definition of terms used

Burst breakpoint
:   Boundary that AXI5 bursts cannot cross.

    These boundaries can be the following:

    - 1KB address boundary: DMA-350 never crosses 1KB address boundaries (AHB requirement support).
    - Trigger block end: Flow trigger requests enable a trigger block to be accessed. Once the access is complete, a new trigger request is required to access any further data so AXI5 bursts cannot go beyond trigger blocks.
    - FIFO size/2 limits the amount of data transferred by a burst.
    - MAXBURST register setting limits the burst length (axlen): the burst must be shorter than this user-specified value

Unaligned start
:   First accessed byte of an AXI5 transaction is not the LSB byte lane of the bus.

Unaligned end
:   Last accessed byte of an AXI5 transaction is not the MSB byte lane of the bus.

DMA-350 has two modes to determine the transfer size of its AXI5 burst beats (axsize):

Unoptimized
:   Beat size is the same as set in DMA command regardless of bus width.

Optimized
:   To optimize bus utilization for narrow transfers, they are grouped into wider accesses, when possible. The AXI5 protocol specification offers different possibilities for read and write side.

    - For write side, beat size is the same as bus width, write strobes are used to exclude unaccessed byte lanes from write.
    - For read side, beat size is the same as bus width for an AXI5 transaction with aligned end. AXI5 transaction with unaligned end may only be partially optimized. See the examples in [Example of an unaligned start address](/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Example-of-an-unaligned-start-address?lang=en "Assuming the following settings:") and [Example of an unaligned end address](/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Example-of-an-unaligned-end-address?lang=en "Assume the following settings:").

### Optimization requirements

- AXI5 subordinate targeted by AXI5 bursts must be of normal memory type (not device).
- Template feature must be disabled for current DMA command on current side.
- Address increment must be 1 for current DMA command on current side.
- Read:

  - AXI transaction either contains enough data to reach bus alignment or has an aligned start.
  - If start is aligned, but not enough data to access all bytes on the bus, largest possible arsize is used that stays within the address space defined by the DMA command.
