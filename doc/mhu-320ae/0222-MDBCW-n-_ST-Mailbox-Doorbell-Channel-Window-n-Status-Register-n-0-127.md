# MDBCW<n>_ST, Mailbox Doorbell Channel Window <n> Status Register, n = 0 - 127

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--ST--Mailbox-Doorbell-Channel-Window--n--Status-Register--n---0---127>

### MDBCW<n>\_ST, Mailbox Doorbell Channel Window <n> Status Register, n = 0 - 127

Returns doorbell channel flags

### Configurations

This register is present only when DBE is implemented. Otherwise, direct accesses to MDBCW<n>\_ST are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   (32 \* n) + 0x1000

### Bit descriptions

Figure 1. MHUR.MBX\_MDBCW<n>\_ST bit assignments

![mhur.mbx_mdbcw_n__st bit assignments](images/0222-MDBCW-n-_ST-Mailbox-Doorbell-Channel-Window-n-Status-Register-n-0-127-img01.svg)

<table id="mhur_mbx_mdbcw_n__st__amdbcwn_st-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MDBCW&lt;n&gt;_ST bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d127611e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d127611e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d127611e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d127611e163" rowspan="1">
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
     Indicates the status of Flag bit &lt;x&gt; of the DBCH
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Flag&lt;x&gt; bit is not set
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Flag&lt;x&gt; bit is set
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000
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
   <th class="documents-nocellnorowborder" colspan="1" id="d127611e253" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d127611e256" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d127611e259" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d127611e262" rowspan="1">
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
    (32 * n) + 0x1000
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MDBCW&lt;n&gt;_ST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
