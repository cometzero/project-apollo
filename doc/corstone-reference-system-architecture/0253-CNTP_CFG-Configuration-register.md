# CNTP_CFG, Configuration register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-timer-programmers-model/CNTP-CFG--Configuration-register>

### CNTP\_CFG, Configuration register

Provides timer configuration information.

The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTP_CFG register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d126551e70" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126551e74" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126551e78" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126551e82" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126551e86" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d126551e91" rowspan="1">
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
     31:4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     28
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     AIVAL
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Indicates whether Automatic Increment is implemented. Permitted values are:
    </p>
    <ul>
     <li>
      <p>
       0000: Automatic Increment is not implemented.
      </p>
     </li>
     <li>
      <p>
       0001: Automatic Increment is implemented. All other values are Reserved.
      </p>
     </li>
    </ul>
   </td>
  </tr>
 </tbody>
</table>
