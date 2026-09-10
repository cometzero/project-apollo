# Trigger matrix for selectable sources

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-matrix-for-selectable-sources>

### Trigger matrix for selectable sources

The DMA-350 implements a trigger matrix for both trigger inputs and outputs as each trigger can be assigned to a channel based on the register settings. The trigger matrix can also create a connection between one channel’s trigger output and another channel’s trigger input port to have internal events starting triggers.

The number of trigger inputs can be configurable and can be different than the number of channels. The SW is able to select trigger inputs for channels using the trigger matrix.

The DMA-350 manages the selection procedure and only allows valid connections between triggers and channels. The security attribute of the channels and the trigger ports are checked and a trigger port cannot be selected by more than one channel at the same time. There are scenarios when the external trigger ports are not selected,but are still busy with handling requests because of software intervention. These scenarios are also covered by the matrix and the trigger ports are not selectable until the software intervention side effects are settled.

The trigger input selection can result in an error if the trigger input interface is not selectable for the following reasons:

- It is used by a different channel.
- Trigger port is not selected, but more than one channel tries to select it in the same cycle.
- Not allowed for selection because of security attribute differences.
- Trigger in interface is not in IDLE because of an ongoing software initiated clear handshake.
- When using internal triggers, the trigger input port cannot be connected to the trigger output port of the same channel.

The trigger output selection can result in an error in case the trigger output interface is not selectable for the following reasons:

- It is used by a different channel.
- Trigger port is not selected, but more than one channel tries to select it in the same cycle.
- Not allowed for selection because of security attribute differences of the channel and the trigger port.
- Trigger out interface is not in IDLE because of a previously unfinished trigger handshake. This might be a pending req not receiving and ack or an ack stuck HIGH at the end of the handshake.
- When using internal triggers, the trigger output port cannot be connected to the trigger input port of the same channel.
