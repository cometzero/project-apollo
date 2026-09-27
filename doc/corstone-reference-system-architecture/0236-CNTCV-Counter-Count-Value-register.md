# CNTCV, Counter Count Value register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-counter-Programmers-model/CNTCV--Counter-Count-Value-register>

### CNTCV, Counter Count Value register

The CNTCV register indicates the current count value. The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTCV register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d110488e62" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d110488e66" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d110488e70" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d110488e74" rowspan="1">
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
     63:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CountValue
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
    </p>
    <ul>
     <li>
      RO from CNT ReadBase
     </li>
     <li>
      RW from CNT ControlBase
     </li>
    </ul>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Indicates the count value.
    </p>
   </td>
  </tr>
 </tbody>
</table>
