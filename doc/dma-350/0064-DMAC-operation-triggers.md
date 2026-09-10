# DMAC operation triggers

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers>

### DMAC operation triggers

Trigger inputs and outputs can synchronize activities within a system without SW intervention. The DMAC can have trigger inputs and outputs on a channel basis when enabled. The input triggers support multiple modes for different purposes, while the output triggers be used to mark the final step of a complete DMAC operation. The trigger matrix part of the DMA-350 handles the connections between the external trigger ports and the DMA channels, making it possible for the DMA channels to select which trigger ports to use or which other DMA channel to connect to.

- **[Trigger inputs](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-inputs?lang=en)**
   Trigger input ports use the trigger signals to enable peripherals to communicate with the DMAC and sequence DMAC operations without SW intervention. Triggers provide flow control for transfers within a DMAC operation and can also be used to start entire DMAC operations. The mode in which the trigger input is used can be selected through configurable registers.
- **[Trigger outputs](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-outputs?lang=en)**
   Trigger outputs define the end of the command execution before the DONE interrupt is asserted. They can be used to synchronize activities between HW elements in the system.
- **[Trigger matrix for selectable sources](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-matrix-for-selectable-sources?lang=en)**
   The DMA-350 implements a trigger matrix for both trigger inputs and outputs as each trigger can be assigned to a channel based on the register settings. The trigger matrix can also create a connection between one channel’s trigger output and another channel’s trigger input port to have internal events starting triggers.
- **[Internal trigger connection](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Internal-trigger-connection?lang=en)**
   The DMA-350 enables synchronization of two channels by internal trigger connection. The trigger output port of a channel (sending channel) can be internally connected to a trigger input port of another channel (receiving channel). The req on the trigger output port signals the finish of a command and starts the operation of another command on the receiving channel.
- **[Software triggers](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers?lang=en)**
   The software Trigger Interfaces are provided to enable the software to interact with triggering. They can be used for synchronizing the DMAC operation with the software, or during development, it can be a substitute for hardware trigger events.
