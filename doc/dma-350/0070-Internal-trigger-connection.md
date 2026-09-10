# Internal trigger connection

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Internal-trigger-connection>

### Internal trigger connection

The DMA-350 enables synchronization of two channels by internal trigger connection. The trigger output port of a channel (sending channel) can be internally connected to a trigger input port of another channel (receiving channel). The req on the trigger output port signals the finish of a command and starts the operation of another command on the receiving channel.

A channel that is using internal triggering is always in command trigger mode regardless of the configured trigger type.

The sending channel is waiting for the trigger ack from the receiving channel. When the receiving channel is configured to command trigger, the ack is deasserted right after the sending channel deasserts the req. This means the sending channel can continue with a new command when the receiving channel started its command.

A chain of more than two channels with internally connected triggers can be formed. A closed loop can be formed from such connected channels. In such a case, software trigger can be used to start the very first operation of the chain.

When the number of channels is only one, internal triggering cannot be used. If internal hardware trigger mode is configured, it is treated as external hardware trigger mode.
