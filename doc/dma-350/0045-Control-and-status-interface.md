# Control and status interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface>

### Control and status interface

The control and status interface makes system control of the DMAC operation (stop and pause) possible and provides status information of the DMAC operation.

- **[General purpose outputs](/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/General-purpose-outputs?lang=en)**
   The General Purpose Output (GPO) ports provide extra bits that you can set to a stable value throughout a DMAC operation.
- **[Stop and pause control](/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Stop-and-pause-control?lang=en)**
   The allch\_stop signals can be used to stop the operation of all the active channels of the DMAC by an external hardware unit. The stop function can be useful when dealing with error scenarios in the system and immediate action must clear the DMAC tasks.
- **[Cross Trigger Interface](/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Cross-Trigger-Interface?lang=en)**
   The DMAC provides a Cross Trigger Interface (CTI) that allows pausing and resuming all channels at once. The CTI is required in a system where a processor is halted for debug purposes and the debugger must save the actual memory contents so the DMAC can also be paused to avoid corrupting the current state of the system.
- **[Status signals](/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Status-signals?lang=en)**
   These signals indicate different status of the individual channels:
