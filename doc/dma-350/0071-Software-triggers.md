# Software triggers

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers>

### Software triggers

The software Trigger Interfaces are provided to enable the software to interact with triggering. They can be used for synchronizing the DMAC operation with the software, or during development, it can be a substitute for hardware trigger events.

- **[Software Trigger Interface](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers/Software-Trigger-Interface?lang=en)**
   The software Trigger Interface consists of the following DMA channel register fields.
- **[Software trigger protocol](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers/Software-trigger-protocol?lang=en)**
   The wait status fields (STAT\_\*WAIT) indicate when the DMA channel can accept a software trigger. Software triggers cannot be initiated when the wait status field is zero.
- **[Software trigger interrupts](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers/Software-trigger-interrupts?lang=en)**
   The INTR\_\* interrupt status fields are set whenever the corresponding STAT\_\* fields are set and the corresponding interrupt is enabled by INTREN\_\* being set to 1.
