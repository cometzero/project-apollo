# DMA interrupts

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/DMA-interrupts>

### DMA interrupts

Interrupts provide indication of internal state changes of the DMA channel and the DMA unit as well. Each channel has its own separate interrupt. One global Non-secure interrupt is always present and, in addition, one global Secure interrupt and one Secure violation interrupt also appear when TrustZone support is enabled. Interrupts are level-based signals.
