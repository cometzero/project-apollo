# Stop and pause control

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Control-and-status-interface/Stop-and-pause-control>

### Stop and pause control

The allch\_stop signals can be used to stop the operation of all the active channels of the DMAC by an external hardware unit. The stop function can be useful when dealing with error scenarios in the system and immediate action must clear the DMAC tasks.

The stop waits for all the outstanding responses from read and write transactions but it tries to finish the channel operation as soon as possible by not sending more requests out and not asserting triggers.

These signals are built up from a simple 4-phase handshake. When the allch\_stop\_req\_nonsec is asserted, all Non-secure channels that are not in IDLE are stopped. The software can enable channels but they are immediately stopped when this request is asserted. The assertion of allch\_stop\_ack\_nonsec signals that all Non-secure channels have been stopped or are inactive. When the security option is enabled (SECEXT\_PRESENT=1) separate signals, allch\_stop\_req\_sec and allch\_stop\_ack\_sec, exist for the Secure channels that operate on the channels in the Secure domain only.

The operation of the DMA channels can be paused immediately at a point in time by the allch\_pause signals operated by an external hardware unit. The pause function can be useful to freeze the channel in a state and check the current values of its registers, or to pause the DMA unit for a while to free up bus infrastructure resources. The enable bit remains asserted and every transfer and trigger state are kept, no information is lost. These signals are built up from a simple 4-phase handshake. When the allch\_pause\_req\_nonsec asserted, all Non-secure channels that are not in IDLE are paused.

The software can enable channels but they are immediately paused when this request is asserted. When the request is deasserted, the operation continues. When the allch\_pause\_ack\_nonsec asserted, all Non-secure channels are paused or inactive. When the security option is enabled (SECEXT\_PRESENT=1) separate signals, allch\_pause\_req\_sec and allch\_pause\_ack\_sec, exist for the Secure channels that operate on the channels in the Secure domain only.
