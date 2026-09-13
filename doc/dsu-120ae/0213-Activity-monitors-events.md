# Activity monitors events

Source: <https://developer.arm.com/documentation/107721/0001/Activity-Monitors-Extension-support/Activity-monitors-events>

### Activity monitors events

Activity monitors events in the DynamIQ™ Shared Unit-120AE are all fixed, and they map to the activity monitors counters.

The following table shows the mapping of counters to fixed events.

<table id="dpr1660577319238__table_w3017ab1b9b1b3_w3018ab1b9b1_w3019ab1b9_w3020ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Mapping of counters to fixed events
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
   <th class="documents-nocellnorowborder" colspan="1" id="d4348e77" rowspan="1">
    Activity monitor counter &lt;n&gt;
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d4348e80" rowspan="1">
    Associated register
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d4348e83" rowspan="1">
    Event
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d4348e86" rowspan="1">
    Event number
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d4348e89" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AMEVCNTR0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CLUSTERAMU_AMEVCNTR0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3_CACHE_READ_HIT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 cache read hit
    </p>
    <blockquote id="dpr1660577319238__note_w3021ab1b9b1b3b3c13b1b9b3_w3022ab1b9b1b3b3c13b1b9_w3023ab1b9b1b3b3c13b1_w3024ab1b9b1b3b3c13_w3025ab1b9b1b3b3_w3026ab1b9b1b3_w3027ab1b9b1_w3028ab1b9_w3029ab1" title="Note info">
     <h3 class="documents-underline">
      Note
     </h3>
     This event counts the same information as the IMP_CLUSTERL3HIT_EL1 System register.
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AMEVCNTR1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CLUSTERAMU_AMEVCNTR1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3_CACHE_READ_MISS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 cache read miss
    </p>
    <blockquote id="dpr1660577319238__note_w3030ab1b9b1b3b3c13b3b9b3_w3031ab1b9b1b3b3c13b3b9_w3032ab1b9b1b3b3c13b3_w3033ab1b9b1b3b3c13_w3034ab1b9b1b3b3_w3035ab1b9b1b3_w3036ab1b9b1_w3037ab1b9_w3038ab1" title="Note info">
     <h3 class="documents-underline">
      Note
     </h3>
     This event counts the same information as the IMP_CLUSTERL3MISS_EL1 System register.
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AMEVCNTR2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CLUSTERAMU_AMEVCNTR2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    POST_L3_READ_OCCUPANCY
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Post L3 read occupancy
    </p>
    <p>
     Increments by n every cycle, where n is the number of Cacheable read transactions outstanding to the bus
     <span class="documents-keyword">
      requester
     </span>
     ports and peripheral port for that cycle.
    </p>
    <p>
     You can use the value n to determine the average latency of a read by dividing by the post-L3 read transaction count.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AMEVCNTR3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CLUSTERAMU_AMEVCNTR3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    POST_L3_WRITE_TRANSACTIONS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Post L3 write transactions
    </p>
    <p>
     Counts the number of Cacheable write transactions that are sent to the bus
     <span class="documents-keyword">
      requester
     </span>
     ports and peripheral port.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    AMEVCNTR4
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERAMU_AMEVCNTR4
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    POST_L3_READ_TRANSACTIONS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Post L3 read transactions
    </p>
    <p>
     Counts the number of Cacheable read transactions that are sent to the bus
     <span class="documents-keyword">
      requester
     </span>
     ports and peripheral port.
    </p>
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> Transactions caused by atomic instructions that perform a read and a write are only counted once, as a read, for the activity monitors. Examples of these instructions include, atomic load, swap, and compare and swap instructions. Atomic store instructions are counted only as a write.
