# CNTP_CTL, Counter-timer Physical Timer Control register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-timer-programmers-model/CNTP-CTL--Counter-timer-Physical-Timer-Control-register>

### CNTP\_CTL, Counter-timer Physical Timer Control register

The CNTP\_CTL register is a control register for the timer. The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTP_CTL register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d38308e65" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d38308e69" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d38308e73" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d38308e77" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d38308e81" rowspan="1">
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
     31:3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RAZ/WI
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ISTATUS
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
      0xX
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The status of the timer. This bit indicates whether the timer condition is met:
    </p>
    <ul>
     <li>
      <p>
       0: Timer condition is not met.
      </p>
     </li>
     <li>
      <p>
       1: Timer condition is met.
      </p>
     </li>
    </ul>
    <p>
     When the value of the ENABLE bit is 1, ISTATUS indicates whether the timer condition is met.
    </p>
    <p>
     ISTATUS takes no account of the value of the IMASK bit. If the value of ISTATUS is 1 and the value of IMASK is 0, then the timer interrupt is asserted.
    </p>
    <p>
     When the value of the ENABLE bit is 0, the ISTATUS field is
     <span class="documents-archterm">
      UNKNOWN
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMASK
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xX
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer interrupt mask bit. Permitted values are:
    </p>
    <ul>
     <li>
      <p>
       0: The IMASK bit masks the Timer interrupt.
      </p>
     </li>
     <li>
      <p>
       1: The IMASK bit masks the Timer interrupt.
      </p>
     </li>
    </ul>
    <p>
     For more information, see the description of the ISTATUS bit.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     ENABLE
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
      0x0
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Enables the timer. Permitted values are:
    </p>
    <ul>
     <li>
      <p>
       0: Timer is disabled.
      </p>
     </li>
     <li>
      <p>
       1: Timer is enabled.
      </p>
     </li>
    </ul>
    <p>
     Setting this bit to 0 disables the timer output signal, but the timer value accessible from CNTP_TVAL continues to count down.
    </p>
    <p>
     Disabling the output signal might be a power‑saving option.
    </p>
   </td>
  </tr>
 </tbody>
</table>
