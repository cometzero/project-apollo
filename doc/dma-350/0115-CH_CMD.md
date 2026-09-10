# CH_CMD

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-CMD>

### CH\_CMD

The Channel DMA Command register allows the SW to control the operation of a DMA command.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMACH<n>

Offset
:   0x000

Type
:   RW

Default
:   0x00000000

### Usage constraints

There are no usage constraints apart from what is described for the block as a whole.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CH_CMD register bit descriptions
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d25471e126" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25471e130" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25471e134" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25471e138" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d25471e142" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [31:25]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [24]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SWTRIGOUTACK
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Software Generated Trigger Output Acknowledge. Write &lsquo;1&rsquo; to acknowledge a Trigger Output request from the DMA. Once set to &lsquo;1&rsquo;, this remains high until the DMA Trigger Output is raised (either on the trigger output signal or as an interrupt) and the acknowledge is accepted. When the channel is not enabled, write to this register is ignored.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [23]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [22:21]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DESSWTRIGINTYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Software Generated Destination Trigger Input Request Type. | RW |
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
    <p>
     Selects the trigger request type for the destination trigger input when the SW triggers the DESSWTRIGINREQ bit.
    </p>
    <ul>
     <li>
      <p>
       00: Single request
      </p>
     </li>
     <li>
      <p>
       01: Last single request
      </p>
     </li>
     <li>
      <p>
       10: Block request
      </p>
     </li>
     <li>
      <p>
       11: Last block request
      </p>
     </li>
    </ul>
    <p>
     This field cannot be changed while the DESSWTRIGINREQ bit is set. The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: (1) &amp; (NUM_TRIGGER_IN &gt; 0)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <code>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|
     </code>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [20]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DESSWTRIGINREQ
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Software Generated Destination Trigger Input Request. Write to &lsquo;1&rsquo; to create a SW trigger request to the DMA with the specified type in the DESSWTRIGINTYPE register. Once set to &lsquo;1&rsquo;, this remains high until the DMA is accepted the trigger and returns this to &lsquo;0&rsquo;. It is also cleared automatically if the current command is completed without expecting another trigger event. When the channel is not enabled, write to this register is ignored.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [19]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [18:17]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SRCSWTRIGINTYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Software Generated Source Trigger Input Request Type.
    </p>
    <p>
     Selects the trigger request type for the source trigger input when the SW triggers the SRCSWTRIGINREQ bit.
    </p>
    <ul>
     <li>
      <p>
       00: Single request
      </p>
     </li>
     <li>
      <p>
       01: Last single request
      </p>
     </li>
     <li>
      <p>
       10: Block request
      </p>
     </li>
     <li>
      <p>
       11: Last block request
      </p>
     </li>
    </ul>
    <p>
     This field cannot be changed while the SRCSWTRIGINREQ bit is set. The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: (1) &amp; (NUM_TRIGGER_IN &gt; 0)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [16]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SRCSWTRIGINREQ
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Software Generated Source Trigger Input Request. Write to &lsquo;1&rsquo; to create a SW trigger request to the DMA with the specified type in the SRCSWTRIGINTYPE register. Once set to &lsquo;1&rsquo;, this remains high until the DMA accepted the trigger and returns this to &lsquo;0&rsquo;. It is also cleared automatically if the current command is completed without expecting another trigger event. When the channel is not enabled, write to this register is ignored.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [15:6]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [5]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RESUMECMD
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Resume Current DMA Operation. Writing this bit to &lsquo;1&rsquo; means that the DMAC can continue the operation of a paused channel. Can be set to &lsquo;1&rsquo; when the PAUSECMD or a STAT_DONE assertion with DONEPAUSEEN set HIGH results in pausing the current DMA channel operation indicated by the STAT_PAUSED and STAT_RESUMEWAIT bits. Otherwise, writes to this bit are ignored.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [4]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PAUSECMD
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Pause Current DMA Operation. Once set to &lsquo;1&rsquo; the status cannot change until the DMA operation reached the paused state indicated by the STAT_PAUSED and STAT_RESUMEWAIT bits. The bit can be set by SW by writing it to &lsquo;1&rsquo;, the current active DMA operation is paused as soon as possible, but the ENABLECMD bit remains HIGH to show that the operation is still active. Cleared automatically when STAT_RESUMEWAIT is set and the RESUMECMD bit is written to &lsquo;1&rsquo;, meaning that the SW continues the operation of the channel. Note that each DMA channel can have other sources of a pause request and this field does not reflect the state of the other sources. When set at the same time as ENABLECMD or when the channel is not enabled then write to this register is ignored.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [3]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     STOPCMD
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Stop Current DMA Operation. Once set to &lsquo;1&rsquo;, this remains high until the DMA channel is stopped cleanly. Then this returns to &lsquo;0&rsquo; and ENABLECMD is also cleared. When set at the same time as ENABLECMD or when the channel is not enabled then write to this register is ignored. Note that each DMA channel can have other sources of a stop request and this field does not reflect the state of the other sources.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [2]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DISABLECMD
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Disable DMA Operation at the end of the current DMA command operation. Once set to &lsquo;1&rsquo;, this field stays high and the current DMA command is allowed to complete, but the DMA does not fetch the next linked command or auto-restarts the DMA command even if they are set. Once the DMA has stopped, it returns to &lsquo;0&rsquo; and ENABLECMD is also cleared. When set at the same time as ENABLECMD or when the channel is not enabled then write to this register is ignored.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [1]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CLEARCMD
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DMA Clear command. When set to &lsquo;1&rsquo;, it remains high until all DMA channel registers and any internal queues and buffers are cleared, before returning to &lsquo;0&rsquo;. When set at the same time as ENABLECMD or while the DMA channel is already enabled, the clear only occurs after any ongoing DMA operation is either completed, stopped or disabled and the ENABLECMD bit is deasserted by the DMA.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     [0]
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     ENABLECMD
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Channel Enable. When set to &lsquo;1&rsquo;, enables the channel to run its programmed task. When set to &lsquo;1&rsquo;, it cannot be set back to zero, and this field automatically clears to zero when a DMA process is completed. To force the DMA to stop prematurely, you must use CH_CMD.STOPCMD instead.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     W1S
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
