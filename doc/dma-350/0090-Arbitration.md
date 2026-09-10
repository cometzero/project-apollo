# Arbitration

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/Arbitration>

### Arbitration

Channel arbitration is required when multiple channels want to use a single bus interface to send transfers.

Each channel has a register to set the channel’s priority (CH\_CTRL.CHPRIO). The priority register defined in the architecture is connected to the QoS bits on AXI but it also affects the arbitration scheme used for that channel. The SW is responsible for adjusting the priorities of the channels properly as the DMA unit does not know which channel operation is more time critical than the other. The SW can only change the arbitration scheme when a channel is stopped or is in IDLE. The arbitration scheme is simple to allow the SW to adjust it flexibly.

- **[Arbitration requests](/documentation/102482/0000/DMAC-operation/Arbitration/Arbitration-requests?lang=en)**
   The channels can generate requests for arbitration when the following conditions occur.
- **[Arbitration scheme](/documentation/102482/0000/DMAC-operation/Arbitration/Arbitration-scheme?lang=en)**
   This section describes the Least-Recently Granted (LRG) arbitration algorithm.
