# DMA unit configuration

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Configuration/DMA-unit-configuration>

### DMA unit configuration

The following four register frames are associated with the DMA unit:

Security Configuration Register Frame (DMASECCFG)
:   This frame contains registers to configure the security and privilege of each DMA channel, and the security of the external trigger ports.

Secure Control Register Frame (DMASECCTRL)
:   This frame contains status and control registers that affect all channels configured as Secure.

Non-secure Control Register Frame (DMANSECCTRL)
:   This frame contains status and control registers that affect all channels configured as Non-secure.

Information Register Frame (DMAINFO)
:   This frame provides information about the capabilities and parameters of the DMA unit.
