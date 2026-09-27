# WRR, Watchdog Refresh register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-Watchdog-overview/WRR--Watchdog-Refresh-register>

### WRR, Watchdog Refresh register

The WRR register is a refresh register for the Watchdog. Any write to this register causes an explicit watchdog refresh.

The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   WRR register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d84884e65" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84884e69" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84884e73" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d84884e77" rowspan="1">
    <p>
     Function
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     31:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     WRR
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     A write to this location causes the Watchdog to refresh and start a new watch period. A read has no effect and returns 0.
    </p>
   </td>
  </tr>
 </tbody>
</table>
