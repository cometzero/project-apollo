# CNTP_CVAL, Counter-timer Physical Timer CompareValue register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-timer-programmers-model/CNTP-CVAL--Counter-timer-Physical-Timer-CompareValue-register>

### CNTP\_CVAL, Counter-timer Physical Timer CompareValue register

The CNTP\_CVAL register holds the 64‑bit compare value for the timer. The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTP_CVAL register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d76596e65" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d76596e69" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d76596e73" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d76596e77" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d76596e81" rowspan="1">
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
     CompareValue
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000_0000_0000
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Holds the 64‑bit compare value for the timer.
    </p>
    <p>
     When CNTP_CTL.ENABLE is 1, the timer condition is met when (CNTPCT - CompareValue) is greater than zero. This means that CompareValue acts like a 64‑bit counter timer. When the timer condition is met:
    </p>
    <ul>
     <li>
      <p>
       NTP_CTL.ISTATUS is set to 1.
      </p>
     </li>
     <li>
      <p>
       An interrupt is generated if CNTP_CTL.IMASK is 0.
      </p>
     </li>
    </ul>
    <p>
     When CNTP_CTL.ENABLE is 0, the timer condition is not met, but CNTPCT continues to count.
    </p>
   </td>
  </tr>
 </tbody>
</table>
