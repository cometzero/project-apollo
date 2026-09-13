# CTI triggers

Source: <https://developer.arm.com/documentation/107721/0001/Debug/Embedded-Cross-Trigger-overview/CTI-triggers>

### CTI triggers

The Cross Trigger Interfaces (CTIs) each have input and output trigger events that are mapped onto the debug and trace events in the Processing Elements (PEs) and Embedded Logic Analyzers (ELAs). All PEs in the cluster have the same mapping.

### CTI input triggers from each PE

The following table shows how events are mapped onto the CTI input triggers.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Allocation of input debug and trace trigger events from the PE to the CTI
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e85" rowspan="1">
    Trigger number
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e88" rowspan="1">
    Trigger event name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e91" rowspan="1">
    Source
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e94" rowspan="1">
    Destination
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e97" rowspan="1">
    Type
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d92738e101" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cross-halt
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    This trigger event is sent when the PE enters Debug state.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Performance monitors overflow
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    This trigger event is sent when a PMU event counter overflows.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Profiling sample
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    This trigger event is sent when a profiling sample is written out.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ETE trace external output
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ETE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    This trigger event is sent from the ETE trace in the PE to the CTI.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    8-9
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ELA output
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ELA
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    This trigger event is sent from the ELA
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      CTTRIGOUT[1:0]
     </span>
    </span>
    attached to the PE.
   </td>
  </tr>
 </tbody>
</table>

### CTI output triggers from each PE

The following table shows how events are mapped onto CTI output triggers.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Allocation of output debug and trace trigger events from the CTI to the PE
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e280" rowspan="1">
    Trigger number
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e283" rowspan="1">
    Trigger event name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e286" rowspan="1">
    Source
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e289" rowspan="1">
    Destination
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e292" rowspan="1">
    Type
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d92738e296" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Debug request
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Level
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Request the PE to enter Debug state.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Restart request
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Request the PE to exit Debug state.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Generic CTI interrupt
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    GIC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    This trigger event must be sent to the Generic Interrupt Controller (GIC) for the PE.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ETE trace external input
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ETE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    This trigger event is sent to the Embedded Trace Extension (ETE) trace in the PE.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    8-9
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ELA input
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ELA
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    This trigger event is sent to the ELA
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      CTTRIGIN[1:0]
     </span>
    </span>
    attached to the PE.
   </td>
  </tr>
 </tbody>
</table>

### Allocation of cluster CTI trigger inputs

The following table shows how events are mapped onto the cluster CTI input triggers.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   Allocation of input trigger events from the cluster ELA and PMU to the cluster CTI
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e482" rowspan="1">
    Trigger number
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e485" rowspan="1">
    Trigger event name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e488" rowspan="1">
    Source
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e491" rowspan="1">
    Destination
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e494" rowspan="1">
    Type
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d92738e498" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster PMU output
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster PMU
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster CTI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    CTI output trigger events that are mapped onto the trigger events in the cluster PMU.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    8-9
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Cluster ELA output
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Cluster ELA
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Cluster CTI
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    CTI output trigger events that are mapped onto the trigger events in the cluster ELA
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      CTTRIGOUT[1:0]
     </span>
    </span>
    .
   </td>
  </tr>
 </tbody>
</table>

### Allocation of cluster CTI trigger outputs

The following table shows how events are mapped onto the cluster CTI output triggers.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 4.
   </span>
   Allocation of output trigger events from the cluster CTI to the cluster ELA
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e632" rowspan="1">
    Trigger number
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e635" rowspan="1">
    Trigger event name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e638" rowspan="1">
    Source
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e641" rowspan="1">
    Destination
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92738e644" rowspan="1">
    Type
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d92738e648" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0-1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CTIIRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    This trigger event must be sent to the Generic Interrupt Controller (GIC).
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3-7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    8-9
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Cluster ELA input
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Cluster CTI
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Cluster ELA
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Pulse
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    CTI output trigger events that are mapped onto the trigger events in the cluster ELA
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      CTTRIGIN[1:0]
     </span>
    </span>
    .
   </td>
  </tr>
 </tbody>
</table>

### Related concepts

- [Embedded Cross Trigger overview](/documentation/107721/0001/Debug/Embedded-Cross-Trigger-overview?lang=en "The Embedded Cross Trigger (ECT) allows debug events to be sent between Processing Elements (PEs).")
