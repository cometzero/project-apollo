# CNTSCR0, CNTSCR1, Counter Scaling registers

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-counter-Programmers-model/CNTSCR0--CNTSCR1--Counter-Scaling-registers>

### CNTSCR0, CNTSCR1, Counter Scaling registers

The CNTSCR0 and CNTSCR1 registers have the same field definitions as the CNTSCR register. These two extra registers are used to preprogram the scaling values so that when hardware‑based clock switching is implemented there is no need to program the scaling increment value each time when clock is switched.

When read by software, the value read is the value that software has written. In certain cases, for example when CNTCR.SCEN has disabled scaling, the actual increment value that the Counter uses is 1.0.

However, the value that is read from these registers does not reflect this. Therefore, the actual increment value that the Counter uses depends on the programming of these registers, the value of two HW configuration parameters, CNTSC and HWCLKSW, and the value of CNTCR.SCEN.

This implementation enables software to keep the scaling values in these registers unaffected when increment value changes due to Counter disabling.

These registers can only be written when the Counter is disabled (CNTCR.EN=0). The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTSCR* register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d41252e77" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41252e81" rowspan="1">
    <p>
     Name N
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41252e85" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41252e89" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d41252e93" rowspan="1">
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
     ScaleVal
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
      0x0100_0000
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     When counter scaling is enabled, ScaleVal is the amount added to the Counter Count Value for every period of the counter as determined by 1/Frequency from the current operating frequency of the system counter, the counter tick. ScaleVal is expressed as an unsigned fixed-point number with an 8‑bit integer value and a 24‑bit fractional value.
    </p>
    <p>
     The CNTSCR register can only be changed when the counter is disabled, CNTCR.EN=0. If the value of CTNSCR changes when CNTCR.EN==1, then the Counter Count Value becomes
     <span class="documents-archterm">
      UNKNOWN
     </span>
     and remains
     <span class="documents-archterm">
      UNKNOWN
     </span>
     on future ticks of the clock.
    </p>
    <p>
     If CNTSC=0, CNTSCR* are permanently driven to
     <span class="documents-g.number.hex">
      0x0100_0000
     </span>
     .
    </p>
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> If HWCLKSW= 0, CNTSCR1 is permanently driven to 0x0000\_0000.
