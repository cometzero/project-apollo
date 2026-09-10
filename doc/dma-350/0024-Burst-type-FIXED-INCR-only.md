# Burst type (FIXED / INCR only)

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Burst-type--FIXED---INCR-only->

### Burst type (FIXED / INCR only)

The DMA-350 reduces complexity by only sending FIXED and INCR bursts.

FIXED bursts are used when targeting peripherals with FIFOs and the same address is accessed several times. This can be done by setting the increment value to 0.

INCR bursts are used in all other cases and the length of a burst is limited by the \*MAXBURSTLEN register setting. This also reduces the complexity of converting AXI5 transfers to AHB in case the DMAC is connected to an AHB interconnect at some point.
