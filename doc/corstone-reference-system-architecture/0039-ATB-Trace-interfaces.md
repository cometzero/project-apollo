# ATB Trace interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Debug-and-Trace-Related-interfaces/ATB-Trace-interfaces>

### ATB Trace interfaces

When DEBUGLEVEL = 2, CRSAS Ma1 provides interfaces to output trace data to an expansion Trace Port Interface Unit (TPIU). The number and types of interfaces vary depending on the HASCSS configuration as follows:

- When HASCSS = 0 and there can only be one CPU, the processor provides its ITM ATB Trace interface and an ETM ATB Trace interface directly for expansion. The processor’s Trace synchronization and Trigger Interface are also provided for expansion. For more information on these interfaces, see Arm® Cortex®-M55 Processor Technical Reference Manual or the relevant sections of Arm® Cortex®-M85 Processor Technical Reference Manual.

  All interfaces reside in the PD\_DEBUG power domain and reside in the DEBUGCPU0CLK clock domain and nCOLDRESETDEBUGCPU0 reset domain.
- When HASCSS = 1, CRSAS Ma1 provides a single ATB bus interface that is normally expected to connect to an external TPIU. This trace bus is synchronous to DEBUGDEBUGCLK, is reset using nCOLDRESETDEBUG and resides in the PD\_DEBUG power domain.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   ATB Trace interface
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d112376e103" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d112376e107" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d112376e111" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d112376e115" rowspan="1">
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
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       ATVALID
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     A transfer is valid during this cycle. If LOW, all the other ATB signals must be ignored in this cycle.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       ATID[6:0]
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     An ID that uniquely identifies the source of the trace.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       ATBYTE
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      IMPLEMENTATION DEFINED
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The number of bytes on ATDATA to be captured, minus 1. Note that is ATDATA is only eight bits wide, this signal may not exist.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       ATDATA
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      IMPLEMENTATION DEFINED
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Trace data bus.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       ATREADY
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Subordinate is ready to accept data.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AFVALID
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This is the flush signal. All buffers must be flushed because trace capture is about to stop.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AFREADY
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This is a flush acknowledge. Asserted when buffers are flushed.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYNCREQ
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Trace synchronization request trace sinks.
    </p>
   </td>
  </tr>
 </tbody>
</table>

When DEBUGLEVEL < 2 these interfaces might not exist. If they do exist, they are tied or unused.
