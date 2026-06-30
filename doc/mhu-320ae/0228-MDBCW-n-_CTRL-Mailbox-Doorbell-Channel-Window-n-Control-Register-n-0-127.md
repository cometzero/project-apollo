# MDBCW<n>_CTRL, Mailbox Doorbell Channel Window <n> Control Register, n = 0 - 127

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--CTRL--Mailbox-Doorbell-Channel-Window--n--Control-Register--n---0---127>

### MDBCW<n>\_CTRL, Mailbox Doorbell Channel Window <n> Control Register, n = 0 - 127

This register contains control bits for doorbell channels

### Configurations

This register is present only when DBE is implemented. Otherwise, direct accesses to MDBCW<n>\_CTRL are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   (32 \* n) + 0x101C

### Bit descriptions

Figure 1. MHUR.MBX\_MDBCW<n>\_CTRL bit assignments

![mhur.mbx_mdbcw_n__ctrl bit assignments](images/0228-MDBCW-n-_CTRL-Mailbox-Doorbell-Channel-Window-n-Control-Register-n-0-127-img01.svg)

<table id="mhur_mbx_mdbcw_n__ctrl__amdbcwn_ctrl-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MDBCW&lt;n&gt;_CTRL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d27761e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d27761e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d27761e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d27761e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_COMB_EN
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Controls whether events from this Doorbell Channel contribute to the Mailbox Combined interrupt
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Doorbell Channel does not contribute to the Mailbox Combined interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Doorbell Channel contributes to the Mailbox Combined interrupt
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Accessibility
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
   <th class="documents-nocellnorowborder" colspan="1" id="d27761e274" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d27761e277" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d27761e280" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d27761e283" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.MBX
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    (32 * n) + 0x101C
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MDBCW&lt;n&gt;_CTRL
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
