# Power management

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Power-management>

### Power management

The DMA-350 has separate power and clock control management systems.

- **[Power P-Channel](/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Power-management/Power-P-Channel?lang=en)**
   The DMA-350 is using one full LPI P-Channel for power management. The purpose of this feature is to enable lower power states (removing power) to reduce power consumption while not in active use. The power P-Channel is used to control the power state of the DMAC logic.
- **[Clock Q-Channel](/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Power-management/Clock-Q-Channel?lang=en)**
   The DMA-350 is using one full LPI Q-Channel for clock management. The purpose of this feature is to reduce power consumption by shutting down the clock while not in active use. The clock Q-Channel is used to turn on and off the clock for the DMAC logic.
