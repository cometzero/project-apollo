# DMAC operation overview

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-overview>

### DMAC operation overview

The DMAC can be configured by register writes to execute a vast variety of commands. When the software finalizes the register settings and the command link elements, the channel can be enabled by an additional register write. This step makes all configuration registers become read-only from the software side. The DMAC then starts checking the validity of the command and executes the transfers based on the register settings.

The commands can contain simple memory transfers, scatter-gather type transfers, handling of triggers, general purpose outputs, 2D memory operations, and many other combinations. When a command is finished the DMAC either returns to idle, reloads the command or jumps to a next item in a command list. When the DMAC returns to an IDLE state it can generate interrupts and trigger output signals to synchronize this event with SW or other HW elements in the system. When the DMAC is in IDLE, the registers can be configured again.

The DMAC is also prepared to detect errors during the memory transfer. When a fault is received, it returns an error and stops its operation.
