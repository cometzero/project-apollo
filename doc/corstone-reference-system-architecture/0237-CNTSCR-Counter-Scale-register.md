# CNTSCR, Counter Scale register

Source: <https://developer.arm.com/documentation/102803/latest/System-timer-components/System-counter-Programmers-model/CNTSCR--Counter-Scale-register>

### CNTSCR, Counter Scale register

The CNTSCR registers store the Counter Scaling value. The following table shows the bit assignments.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CNTSCR register bit assignments
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
   <th class="documents-nocellnorowborder" colspan="1" id="d36468e65" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d36468e69" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d36468e73" rowspan="1">
    <p>
     Access
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d36468e77" rowspan="1">
    <p>
     Reset value
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d36468e81" rowspan="1">
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
     When counter scaling is enabled, ScaleVal is the amount added to the Counter Count Value for every period of the counter as determined by 1/Frequency from the current operating frequency of the system counter, the counter tick.
    </p>
    <p>
     ScaleVal is expressed as an unsigned fixed‑point number with an 8‑bit integer value and a 24‑bit fractional value.
    </p>
    <p>
     The CNTSCR register can only be changed when the counter is disabled, that is, CNTCR.EN=0. If the value of CTNSCR changes when CNTCR.EN==1, then the Counter Count Value becomes
     <span class="documents-archterm">
      UNKNOWN
     </span>
     and remains
     <span class="documents-archterm">
      UNKNOWN
     </span>
     on future ticks of the clock.
    </p>
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> If CNTSC=0, CNTSCR is permanently driven to 0x0100\_0000.
