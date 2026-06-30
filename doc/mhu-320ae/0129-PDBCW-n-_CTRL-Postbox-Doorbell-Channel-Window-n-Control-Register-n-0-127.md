# PDBCW<n>_CTRL, Postbox Doorbell Channel Window <n> Control Register, n = 0 - 127

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--CTRL--Postbox-Doorbell-Channel-Window--n--Control-Register--n---0---127>

### PDBCW<n>\_CTRL, Postbox Doorbell Channel Window <n> Control Register, n = 0 - 127

This register contains control bits for doorbell channels

### Configurations

This register is present only when DBE is implemented. Otherwise, direct accesses to PDBCW<n>\_CTRL are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (32 \* n) + 0x101C

### Bit descriptions

Figure 1. MHUS.PBX\_PDBCW<n>\_CTRL bit assignments

![mhus.pbx_pdbcw_n__ctrl bit assignments](images/0129-PDBCW-n-_CTRL-Postbox-Doorbell-Channel-Window-n-Control-Register-n-0-127-img01.svg)

<table id="mhus_pbx_pdbcw_n__ctrl__apdbcwn_ctrl-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PDBCW&lt;n&gt;_CTRL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d105284e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d105284e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d105284e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d105284e163" rowspan="1">
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
    PBX_COMB_EN
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Controls whether events from this Doorbell Channel contribute to the Postbox Combined interrupt
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Doorbell Channel does not contribute to the Postbox Combined interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Doorbell Channel contributes to the Postbox Combined interrupt
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
   <th class="documents-nocellnorowborder" colspan="1" id="d105284e274" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d105284e277" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d105284e280" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d105284e283" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUS.PBX
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    (32 * n) + 0x101C
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PDBCW&lt;n&gt;_CTRL
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
