# CNTCR, Counter Control register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-counter-Programmers-model/CNTCR--Counter-Control-register>

### CNTCR, Counter Control register

The CNTCR register enables the counter, controls the counter frequency setting, and controls counter behavior during debug.

The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTCR register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d48339e68" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48339e72" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48339e76" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48339e80" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d48339e84" rowspan="1">
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
     31:6
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
     5
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     INTRCLR
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
      0x0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Interrupt clear bit, only writes of 0 are permitted, and writes of 1 are ignored.
    </p>
    <p>
     If APB logic is powered off when the interrupt output is asserted, this bit is cleared automatically. Therefore, it is the responsibility of software to ensure that there is no pending interrupt before powering off the APB logic.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PSLVERRDIS
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
      0x0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PSLVERR output disable:
    </p>
    <ul>
     <li>
      <p>
       0: PSLVERR permanently driven to &lsquo;0&rsquo;.
      </p>
     </li>
     <li>
      <p>
       1: PSLVERR output that the System Counter generates dynamically.
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     INTRMASK
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
      0x0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Interrupt mask:
    </p>
    <ul>
     <li>
      <p>
       0: Interrupt output disabled.
      </p>
     </li>
     <li>
      <p>
       1: Interrupt output enabled.
      </p>
     </li>
    </ul>
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
     SCEN
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
      0x0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Scale enable:
    </p>
    <ul>
     <li>
      <p>
       0: Scaling is not enabled. The Counter value is incremented by &gt;
       <span class="documents-g.number.hex">
        0x01
       </span>
       .000000 for each counter tick.
      </p>
     </li>
     <li>
      <p>
       1: Scaling is enabled. The counter is incremented by the ScaleVal for &gt; each counter tick.
      </p>
     </li>
    </ul>
    <p>
     The ScaleVal value that the System Counter uses is from CNTSCR, CNTSCR[0], or CNTSCR[1]. See
     <a class="document-topic" document-topic-path="/102803/0000/System-timer-components/System-counter-Programmers-model/CNTSCR0--CNTSCR1--Counter-Scaling-registers?lang=en" href="/documentation/102803/0000/System-timer-components/System-counter-Programmers-model/CNTSCR0--CNTSCR1--Counter-Scaling-registers?lang=en" title="The CNTSCR0 and CNTSCR1 registers have the same field definitions as the CNTSCR register. These two extra registers are used to preprogram the scaling values so that when hardware‑based clock switching is implemented there is no need to program the scaling increment value each time when clock is switched.">
      CNTSCR0, CNTSCR1, Counter Scaling registers
     </a>
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
     HDBG
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
      0x0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Halt On Debug:
    </p>
    <ul>
     <li>
      <p>
       0: HALTREQ signal into the Counter has no effect.
      </p>
     </li>
     <li>
      <p>
       1: HALTREQ signal into the Counter halts the Count.
      </p>
     </li>
    </ul>
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
     EN
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
     Enable Counter:
    </p>
    <ul>
     <li>
      <p>
       0: Disabled: Count is not incrementing.
      </p>
     </li>
     <li>
      <p>
       1: Enabled: Count is incrementing.
      </p>
     </li>
    </ul>
   </td>
  </tr>
 </tbody>
</table>
