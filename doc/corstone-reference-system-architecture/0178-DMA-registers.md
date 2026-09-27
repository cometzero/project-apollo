# DMA registers

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/DMA-registers>

### DMA registers

CRSAS Ma1 implements up to one DMA-350. See Arm® CoreLink™ DMA-350 Controller Technical Reference Manual for full details of the DMA software interface. Security and privilege checking of accesses to DMA registers are handled by the DMA.

The DMA resides in the PD\_SYS power domain and is reset by nWARMRESETSYS.
