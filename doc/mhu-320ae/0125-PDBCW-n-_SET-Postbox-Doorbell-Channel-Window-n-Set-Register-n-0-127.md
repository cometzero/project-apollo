# PDBCW<n>_SET, Postbox Doorbell Channel Window <n> Set Register, n = 0 - 127

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--SET--Postbox-Doorbell-Channel-Window--n--Set-Register--n---0---127>

### PDBCW<n>\_SET, Postbox Doorbell Channel Window <n> Set Register, n = 0 - 127

Allows setting doorbell channel flags

### Configurations

This register is present only when DBE is implemented. Otherwise, direct accesses to PDBCW<n>\_SET are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (32 \* n) + 0x100C

### Bit descriptions

Figure 1. MHUS.PBX\_PDBCW<n>\_SET bit assignments

![mhus.pbx_pdbcw_n__set bit assignments](images/0125-PDBCW-n-_SET-Postbox-Doorbell-Channel-Window-n-Set-Register-n-0-127-img01.svg)

<table id="mhus_pbx_pdbcw_n__set__apdbcwn_set-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PDBCW&lt;n&gt;_SET bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d19678e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d19678e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d19678e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d19678e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [31:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FLAG&lt;x&gt;
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Writes of 1 cause the associated bit in the PDBCW&lt;n&gt;_ST registers to be set to 1. Writing 0 has no effect on the value of PDBCW&lt;n&gt;_ST.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Sets the associated bit in the PDBCW&lt;n&gt;_ST register to 1
      </p>
     </dd>
    </dl>
    <p>
     Field always reads as 0
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mhus_pbx_pdbcw_n__set__bits-31-0-reset-9">
     32{x}
    </code>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d19678e256" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d19678e259" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d19678e262" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d19678e265" rowspan="1">
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
    (32 * n) + 0x100C
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PDBCW&lt;n&gt;_SET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
