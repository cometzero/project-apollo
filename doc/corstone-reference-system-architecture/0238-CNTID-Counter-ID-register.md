# CNTID, Counter ID register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-counter-Programmers-model/CNTID--Counter-ID-register>

### CNTID, Counter ID register

The CNTID register indicates additional information about Counter Scaling implementation. The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTID register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d130179e65" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d130179e69" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d130179e73" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d130179e77" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d130179e81" rowspan="1">
    <p>
     Function
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     31:20
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     19
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTSCR_OVR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Defined by parameter with a default value of
     <span class="documents-g.number.hex">
      0x0
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Override counter enable condition for writing to CNTSCR* registers:
    </p>
    <ul>
     <li>
      <p>
       0: CNTSCR* can be written only when CNTCR.EN=- 0:
      </p>
     </li>
     <li>
      <p>
       1: CNTSCR* can be written when CNTCR.EN=0 or - 1:
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     18:17
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTSELCLK
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x01
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Indicates the clock source that the Counter is using. Based on the settings for Counter scaling, the Counter increment value is chosen either from one of the CNTSCR registers or is fixed to 1.0 when scaling is disabled:
    </p>
    <ul>
     <li>
      <p>
       0: Invalid status, Counter not incrementing.
      </p>
     </li>
     <li>
      <p>
       1: CLK0 (REFCLK).
      </p>
     </li>
    </ul>
    <p>
     ```
    </p>
    <p>
     ```
    </p>
    <ul>
     <li>
      <p>
       10: CLK1 (FASTCLK).
      </p>
     </li>
     <li>
      <p>
       11: Invalid status, counter not incrementing.
      </p>
     </li>
    </ul>
    <p>
     These bits are only valid when hardware clock switching is implemented (HWCLKSW=1).
    </p>
    <p>
     If HWCLKSW=0, these bits read a constant value of
     <span class="documents-g.number.hex">
      0x01
     </span>
     regardless of the value of TSCLKSEL input and Counter increment value is used from CNTSCR0 or fixed to 1.0 depending on the status of Counter scaling feature.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CNTCS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Defined by parameter with a default value of
    </p>
    <p>
     <span class="documents-g.number.hex">
      0x1
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Indicates whether Clock Switching is implemented:
    </p>
    <ul>
     <li>
      <p>
       0: HW‑based Counter Clock Switching is not implemented.
      </p>
     </li>
     <li>
      <p>
       1: HW‑based Counter Clock Switching is implemented.
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15:4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved
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
     CNTSC
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
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
     Indicates whether Counter Scaling is implemented:
    </p>
    <ul>
     <li>
      <p>
       0000: Counter Scaling is not implemented.
      </p>
     </li>
     <li>
      <p>
       0001: Counter Scaling is implemented. All other values are Reserved
      </p>
     </li>
    </ul>
   </td>
  </tr>
 </tbody>
</table>
