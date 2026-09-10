# Trigger output interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Trigger-Interface/Trigger-output-interface>

### Trigger output interface

The trigger output interface can signal a connected peripheral that DMA-350 finished a command.

This interface is built up from a simple 4-phase handshake. The interface is defined to be easily compatible with existing Trigger Interface types. The 4-phase handshake also allows simple clock domain crossing structures when the interface is used over different asynchronous clock domains.
