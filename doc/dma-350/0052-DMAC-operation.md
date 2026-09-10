# DMAC operation

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation>

### DMAC operation

This section contains an overview of CoreLink DMA-350 operations.

- **[DMAC operation overview](/documentation/102482/0000/DMAC-operation/DMAC-operation-overview?lang=en)**
   The DMAC can be configured by register writes to execute a vast variety of commands. When the software finalizes the register settings and the command link elements, the channel can be enabled by an additional register write. This step makes all configuration registers become read-only from the software side. The DMAC then starts checking the validity of the command and executes the transfers based on the register settings.
- **[DMAC operation basic commands](/documentation/102482/0000/DMAC-operation/DMAC-operation-basic-commands?lang=en)**
   This section contains an overview of DMA-350 operation basic commands.
- **[DMAC operation extended commands](/documentation/102482/0000/DMAC-operation/DMAC-operation-extended-commands?lang=en)**
   This section contains an overview of DMA-350 operation extended commands.
- **[DMAC operation triggers](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers?lang=en)**
   Trigger inputs and outputs can synchronize activities within a system without SW intervention. The DMAC can have trigger inputs and outputs on a channel basis when enabled. The input triggers support multiple modes for different purposes, while the output triggers be used to mark the final step of a complete DMAC operation. The trigger matrix part of the DMA-350 handles the connections between the external trigger ports and the DMA channels, making it possible for the DMA channels to select which trigger ports to use or which other DMA channel to connect to.
- **[AXI4 stream operation](/documentation/102482/0000/DMAC-operation/AXI4-stream-operation?lang=en)**
   To offer flexible data manipulation, the DMA-350 can include an external engine in the dataflow. The data read by the AXI5 manager interface can be sent out through the AXI4 stream interface to, for example, a filter unit. The unit sends back the corrected data to the DMAC and the DMAC writes the modified data to memory through the AXI5.
- **[DMA Channel lifecycle](/documentation/102482/0000/DMAC-operation/DMA-Channel-lifecycle?lang=en)**
   The operation of a DMA channel is shown in the following figure:
- **[Command linking](/documentation/102482/0000/DMAC-operation/Command-linking?lang=en)**
   The command linking feature enables the DMA channels to execute more operations by automatically loading the next commands from the system memory to its configuration registers. This feature makes the DMAC versatile in combining multiple commands in a DMAC transaction.
- **[Arbitration](/documentation/102482/0000/DMAC-operation/Arbitration?lang=en)**
   Channel arbitration is required when multiple channels want to use a single bus interface to send transfers.
- **[DMAC power management and DMAC control](/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control?lang=en)**
   This section describes the DMA-350 power management and configuration.
- **[Initialization](/documentation/102482/0000/DMAC-operation/Initialization?lang=en)**
   The DMAC must be configured to set the security and privilege attributes for each channel and their attached resources before setting the channels for memory transfers. When the configuration is complete, the channel configuration registers are protected against malicious accesses. The security configuration can be locked until the next reset of the DMAC to further protect the security settings. Privilege settings of a channel can be adjusted when the channel is in IDLE. The register settings are automatically cleared when the security or privilege settings of a channel change.
- **[Interrupt operation](/documentation/102482/0000/DMAC-operation/Interrupt-operation?lang=en)**
   Each channel has its own interrupt to indicate state changes within the channel. There are DMA unit level interrupts that show unit level state changes. The SW can enable, disable, or clear the interrupts.
