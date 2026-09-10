# Trigger input interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Trigger-Interface/Trigger-input-interface>

### Trigger input interface

The trigger input interface can synchronize the operation of a DMA command and a peripheral. The peripheral can signal the DMA-350 when a command or part of a command can be started.

This interface is built up from a simple 4-phase handshake with additional qualifier bus signals that define the type of the current request and acknowledge pair. The interface is defined to be easily compatible with existing Trigger Interface types. The 4-phase handshake also allows simple clock domain crossing structures when the interface is used across different asynchronous clock domains.
