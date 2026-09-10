# Software Trigger Interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers/Software-Trigger-Interface>

### Software Trigger Interface

The software Trigger Interface consists of the following DMA channel register fields.

The software trigger control fields in the CH<x>\_CMD register:

- SRCSWTRIGINREQ
- SRCSWTRIGINTYPE
- DESSWTRIGINREQ
- DESSWTRIGINTYPE
- SWTRIGOUTACK

The software trigger status fields in the CH<x>\_STATUS register:

- STAT\_SRCTRIGINWAIT
- STAT\_DESTRIGINWAIT
- STAT\_TRIGOUTACKWAIT

The software trigger interrupt status fields in the CH<x>\_STATUS register:

- INTR\_SRCTRIGINWAIT
- INTR\_DESTRIGINWAIT
- INTR\_TRIGOUTACKWAIT

The software trigger interrupt enables fields in the CH<x>\_INTREN register:

- INTREN\_SRCTRIGINWAIT
- INTREN\_DESTRIGINWAIT
- INTREN\_TRIGOUTACKWAIT
