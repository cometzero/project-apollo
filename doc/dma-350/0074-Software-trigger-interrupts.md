# Software trigger interrupts

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers/Software-trigger-interrupts>

### Software trigger interrupts

The INTR\_\* interrupt status fields are set whenever the corresponding STAT\_\* fields are set and the corresponding interrupt is enabled by INTREN\_\* being set to 1.

The interrupt flags are cleared automatically when the status flags are cleared.
