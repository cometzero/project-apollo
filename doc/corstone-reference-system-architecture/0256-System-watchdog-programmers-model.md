# System watchdog programmers model

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-Watchdog-overview/System-watchdog-programmers-model>

### System watchdog programmers model

This section describes the programmers model of the System Watchdog. The Watchdog includes the following two 4KB register frames:

- Control Frame.
- Refresh Frame.

Configurable parameters control the base addresses of Control and Refresh frames. These parameters provide the flexibility of arranging these two frames within an 8KB memory map that the following table shows.

The following table shows the Base addresses of Control and Refresh frames.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Base addresses of Control and Refresh frames
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
   <th class="documents-nocellnorowborder" colspan="1" id="d39980e79" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d39980e83" rowspan="1">
    <p>
     Start address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d39980e87" rowspan="1">
    <p>
     End address
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d39980e91" rowspan="1">
    <p>
     Size
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Control Frame
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0_0FFF
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     4KB
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Refresh Frame
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0_1000
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0_1FFF
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     4KB
    </p>
   </td>
  </tr>
 </tbody>
</table>
