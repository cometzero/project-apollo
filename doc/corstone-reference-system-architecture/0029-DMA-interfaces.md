# DMA interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/DMA-interfaces>

### DMA interfaces

CRSAS Ma1 supports a DMA in the system and when DMA exists, namely NUMDMA>1, the following interfaces can exist depending on the configuration of the DMA:

- DMA Trigger Interfaces
- DMA General Purpose Output (GPO) Interfaces
- DMA Stream Interfaces

For more information, see Arm® CoreLink™ DMA-350 Controller Technical Reference Manual.

If any DMA interfaces exist, they all reside in the PD\_SYS power domain, run on SYSSYSCLK, and they are on the nWARMRESETSYS reset domain.
