# Trigger input command mode

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-inputs/Trigger-input-command-mode>

### Trigger input command mode

Trigger inputs can be used to initiate full DMA commands. When either source or destination side is set to this mode, the DMA command waits the trigger handshake before it actually starts any memory operation. This is true even if the DMA channel’s enable bit is set. The DMAC waits for both requests to be asserted before acknowledging them to show when the command is really started.

Figure 1. Command trigger for both source and destination

![Command trigger for both source and destination](images/0066-Trigger-input-command-mode-img01.svg)

The figure shows that the destination trigger request is received first. It is not acknowledged until the DMAC also detects the source trigger request. At this point, both source and destination triggers are acknowledged and the DMAC transfers can start. The trigger handshake can return to IDLE at different points in time depending on the driver of the request signal but it does not interfere with the execution of the data transfers. However, the command can only finish when the trigger acknowledge signals are both deasserted.

When either source or destination side is set to command mode triggering, the DMA channel operation waits for the trigger handshake to happen, ack HIGH, to start operation. Without the handshake, the DMAC is in Active waiting state and not sending transfers to the bus interface.

When all command-based trigger input handshakes are done, meaning req and ack are both HIGH, the command execution can start and the DMA channel exits from the waiting state. The DMAC does not accept new trigger requests until the complete DMAC operation lasts.

For command mode triggers, the reqtype[1:0] can take any of the following values: SINGLE / BLOCK / LAST SINGLE / LAST BLOCK.

The acktype[1:0] value of OKAY / LAST OKAY are both valid for command mode triggers. The DMA-350 returns OKAY value. The DMA channel acktype[1:0] value of DENY is not used in case of command triggering.

Both the source and destination side can be set to Hardware/Software controlled command mode. In this mode, the DMA channel waits for trigger to start operation. The trigger input is primarily external hardware trigger.

However, the input trigger requests can be overridden by generating internal trigger request events by writing an SW programmable register. When either type of trigger arrives, the DMA channel starts its operation. If an SW trigger arrives when the command is already running nothing happens. If an HW trigger arrives when the SW already requested a trigger, the HW trigger is left pending. The HW trigger gets serviced when both arrive at the same time.

When the trigger request is deasserted for a command trigger, the DMAC deasserts the acknowledge as soon as possible. This enables the sender of the trigger to continue its operation.

Figure 2. Trigger input ACK assertion and deassertion for command triggers

![Trigger input ACK assertion and deassertion for command triggers](images/0066-Trigger-input-command-mode-img02.svg)

The figure shows the ack deassertion approach of the DMAC when using command triggers:

t0
:   The Trigger Interface is in IDLE.

t1
:   The peripheral requests any type of trigger to start the command.

t2
:   The DMAC accepts the request if the DMA channel is waiting for the trigger and ready to execute the operation.

t3
:   The peripheral deasserts the
    req signal when it receives the OKAY response from the DMAC. The DMAC still executes the requested operation.

t4
:   The DMAC detects that the
    req is deasserted and it deasserts the
    ack so the Trigger Interface returns to IDLE. The command is still running.

t5
:   The command is finished but it is not reflected on the trigger input interface. Trigger out signals can be used to show the end of a command.
