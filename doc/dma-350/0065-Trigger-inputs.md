# Trigger inputs

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-inputs>

### Trigger inputs

Trigger input ports use the trigger signals to enable peripherals to communicate with the DMAC and sequence DMAC operations without SW intervention. Triggers provide flow control for transfers within a DMAC operation and can also be used to start entire DMAC operations. The mode in which the trigger input is used can be selected through configurable registers.

A 4-phase handshake bus is used between the peripheral and the DMA-350. Extra qualifier signals extend the req and ack signal pair in both directions. The requesting peripheral can signal to the DMAC that it has data to be transferred by the req signal. The additional qualifier signals, reqtype, are used to show the DMAC that it has single or block data to be transferred, and that it has the last data amount to be transferred. The different request types can be seen in the following table.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Trigger request types
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d66273e84" rowspan="1">
    <p>
     Value
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d66273e88" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d66273e92" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2&rsquo;b00
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SINGLE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The peripheral can ask for a single beat of the defined transfer size.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2&rsquo;b10
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BLOCK
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The peripheral can ask for a larger block of transfer size elements. The block size is defined in the DMAC and in the peripheral as well and can comprise multiple bursts.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2&rsquo;b01
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     LAST SINGLE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     When the peripheral is the flow controller of the transfer and the DMAC does not know the size of the transferable data, the peripheral can close the transfer by requesting a final single beat.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     2&rsquo;b11
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     LAST BLOCK
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Similar to LAST SINGLE but the final transfer request is the block size defined in the DMAC and the peripheral. This is used when the complete transfer size is divisible by block size operations.
    </p>
   </td>
  </tr>
 </tbody>
</table>

The DMA-350 shows the peripheral that the ack signal received the request. The additional qualifier bus signals, acktype, provide the peripheral with extra information that the trigger request was accepted or not, or if the DMAC transfer is finished after the current transaction.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Trigger acknowledgment types
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d66273e189" rowspan="1">
    <p>
     Value
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d66273e193" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d66273e197" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2&rsquo;b00
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OKAY
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This acknowledge type indicates the DMAC accepted the request type. The DMAC indicates that it executes the transfer, but not necessarily at the time of the acknowledge. The DMAC may accept multiple requests before executing the requested operation.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2&rsquo;b10
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     LAST OKAY
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This acknowledge type indicates that the DMAC accepted the request type and tells the peripheral that this is the final transfer of the operation. This acknowledge type has two purposes:
    </p>
    <ul>
     <li>
      <p>
       The DMAC acknowledges a LAST request from the peripheral to show that both ends are in sync.
      </p>
     </li>
     <li>
      <p>
       The DMAC is the flow controller and tells the peripheral that no more transfers are expected, so the peripheral needs to reset its transfer counters. For example, a shorter burst is sent as a final transfer.
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2&rsquo;b01
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DENY
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This acknowledge type indicates that the DMAC cannot accept this request now. This can be useful when the DMAC is the flow controller and the peripheral requests SINGLE transfers, but the DMAC expects more transfers to accumulate and optimizes for a block transfer. In this case, the DMAC denies the SINGLE requests so that the handshake can go back to IDLE state.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     2&rsquo;b11
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RESERVED
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Not used.
    </p>
   </td>
  </tr>
 </tbody>
</table>

A channel has two trigger input ports when enabled:

- One for source triggering to control read operations.
- One for destination triggering to control write operations.

The number of trigger inputs are configurable and can be different than the number of channels. The SW is able to select trigger inputs for channels using the trigger matrix, see [Trigger matrix for selectable sources](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-matrix-for-selectable-sources?lang=en "The DMA-350 implements a trigger matrix for both trigger inputs and outputs as each trigger can be assigned to a channel based on the register settings. The trigger matrix can also create a connection between one channel’s trigger output and another channel’s trigger input port to have internal events starting triggers.").

When a trigger port is present but SW wants to disable triggering, the triggers can be set to disabled mode for the command in the control register. In this mode, the DMA channel does not wait for any external input to happen and starts execution after the DMAC Enable bit is set.

Trigger input modes are set through SW programmable registers. Trigger related registers can only be adjusted when the DMA channel is idle.

The trigger inputs are connected to the DMA channel after the DMA channel is enabled. The connections are kept until the current command lasts. The triggers are given back to the trigger matrix when all the operations are finished.

When a channel finishes a command, there might be a pending req on the trigger input port used by the channel. This can happen when a trigger request arrives after a command has received all the expected trigger requests and before the trigger input is returned to the trigger matrix.

The req signal on the top-level trigger port remains pending without getting an ack signal. Similarly, when a req signal arrives on a trigger input that is not connected to any channel, it does not get an ack signal, and the req signal remains pending. When a channel is configured to use a trigger input port with pending request, the channel receives the req immediately after channel enable.

In a normal operation, the DMA channel releases the output trigger when the trigger operation is finished. If the channel receives a stop signal and there is already a pending request on the trigger port, the channel releases the port immediately without waiting for the req-ack handshake to complete. The channel is ready to be configured for a new command. However, the DMA-350 waits for the handshake to be finished on the trigger port and no other channel can select this port until then.

When a channel is paused, the pending triggers are left as is, and the service is pending. The interface can stall in any state. During a pause, external signals, like a req signal in the trigger input or an ack signal in the trigger output, can change state. After the channel operation is resumed, the trigger operation continues.

When a DMA channel is stopped, the trigger matrix takes back the control over the trigger input. The channel services an already acknowledged trigger before giving back the control to the matrix. The interface can be left in idle or request state. For the trigger output, the trigger matrix takes back the control and responds to the already pending triggers for the channel by an internal ack signal. The pending external triggers must be served by the trigger matrix by waiting for an ack signal to arrive. After the ack signal has arrived, the req signal is pulled LOW. The interface returns to idle state.

The SW can initiate a trigger request automatic clear. The DMAC can send a “deny” acknowledge to a pending request on a trigger input. This way, the unneeded pending request can be cleared without trigger protocol violation.

> ### Note
>
> For debug purposes, the SW can mimic the external HW trigger. See [Software triggers](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Software-triggers?lang=en "The software Trigger Interfaces are provided to enable the software to interact with triggering. They can be used for synchronizing the DMAC operation with the software, or during development, it can be a substitute for hardware trigger events.") for more information.

- **[Trigger input command mode](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-inputs/Trigger-input-command-mode?lang=en)**
   Trigger inputs can be used to initiate full DMA commands. When either source or destination side is set to this mode, the DMA command waits the trigger handshake before it actually starts any memory operation. This is true even if the DMA channel’s enable bit is set. The DMAC waits for both requests to be asserted before acknowledging them to show when the command is really started.
- **[Trigger input flow control mode](/documentation/102482/0000/DMAC-operation/DMAC-operation-triggers/Trigger-inputs/Trigger-input-flow-control-mode?lang=en)**
   Trigger inputs can also be used for flow control purposes and only enable small parts of a larger command for every trigger. For this mode, the SW must set the trigger size which tells the number of transfer size blocks to be accessed for one trigger event. The source trigger input is used to control the read flow, while the destination trigger input controls the write flow of a DMA operation.
