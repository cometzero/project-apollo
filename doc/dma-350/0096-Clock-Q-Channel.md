# Clock Q-Channel

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Power-management/Clock-Q-Channel>

### Clock Q-Channel

The DMA-350 is using one full LPI Q-Channel for clock management. The purpose of this feature is to reduce power consumption by shutting down the clock while not in active use. The clock Q-Channel is used to turn on and off the clock for the DMAC logic.

The Q-Channel interface controls the DMAC clock management. When the DMAC is active, clock quiescence requests are denied and the operation simply continues. When the DMAC is actively waiting for an event or is inactive, the quiescence request is accepted and the clock can be shut down.

For more information on the Q-Channel handshake mechanism, see the [AMBA® Low Power Interface Specification](https://developer.arm.com/documentation/ihi0068/) document.

For Q-Channel interface signals, see [Signal descriptions](/documentation/102482/0000/Signal-descriptions?lang=en "This appendix contains all signal descriptions.").
