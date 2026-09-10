# Cross Trigger Interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Cross-Trigger-Interface>

### Cross Trigger Interface

The DMAC provides a Cross Trigger Interface (CTI) that allows pausing and resuming all channels at once. The CTI is required in a system where a processor is halted for debug purposes and the debugger must save the actual memory contents so the DMAC can also be paused to avoid corrupting the current state of the system.

The interface consists of a halt request, halt\_req, a restart request, restart\_req, and a status signal showing whether the DMAC has halted, halted.
