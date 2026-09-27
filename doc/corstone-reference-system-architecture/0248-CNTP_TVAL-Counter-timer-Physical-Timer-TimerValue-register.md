# CNTP_TVAL, Counter-timer Physical Timer TimerValue register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-timer-programmers-model/CNTP-TVAL--Counter-timer-Physical-Timer-TimerValue-register>

### CNTP\_TVAL, Counter-timer Physical Timer TimerValue register

The CNTP\_TVAL register holds the timer value for the timer. The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTP_TVAL register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d6197e65" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d6197e69" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d6197e73" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d6197e77" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d6197e81" rowspan="1">
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
     TimerValue
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
      0xXXXX_XXXX
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The TimerValue view of the physical timer. On a read of this register:
    </p>
    <ul>
     <li>
      <p>
       If CNTP_CTL.ENABLE is 0, the value that is returned is
       <span class="documents-archterm">
        UNKNOWN
       </span>
       .
      </p>
     </li>
     <li>
      <p>
       If CNTP_CTL.ENABLE is 1, the value that is returned is (CNTP_CVAL - CNTPCT).
      </p>
     </li>
    </ul>
    <p>
     On a write of this register, CNTP_CVAL is set to (CNTPCT + TimerValue), where TimerValue is treated as a signed 32-bit integer.
    </p>
    <p>
     When CNTP_CTL.ENABLE is 1, the timer condition is met when (CNTPCT - CNTP_CVAL) is greater than zero. This means that TimerValue acts like a 32‑bit downcounter timer. When the timer condition is met:
    </p>
    <ul>
     <li>
      <p>
       CNTP_CTL.ISTATUS is set to 1.
      </p>
     </li>
     <li>
      <p>
       If CNTP_CTL.IMASK is 0, an interrupt is generated.
      </p>
     </li>
    </ul>
    <p>
     When CNTP_CTL.ENABLE is 0, the timer condition is not met, but CNTPCT continues to count, so the TimerValue view appears to continue to count down.
    </p>
   </td>
  </tr>
 </tbody>
</table>
