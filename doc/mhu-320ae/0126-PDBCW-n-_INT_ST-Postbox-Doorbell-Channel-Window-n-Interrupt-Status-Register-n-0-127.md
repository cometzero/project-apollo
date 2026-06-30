# PDBCW<n>_INT_ST, Postbox Doorbell Channel Window <n> Interrupt Status Register, n = 0 - 127

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PDBCW-n--INT-ST--Postbox-Doorbell-Channel-Window--n--Interrupt-Status-Register--n---0---127>

### PDBCW<n>\_INT\_ST, Postbox Doorbell Channel Window <n> Interrupt Status Register, n = 0 - 127

Returns doorbell channel interrupt status

### Configurations

This register is present only when DBE is implemented. Otherwise, direct accesses to PDBCW<n>\_INT\_ST are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (32 \* n) + 0x1010

### Bit descriptions

Shows the status of the events of the DBCH

Figure 1. MHUS.PBX\_PDBCW<n>\_INT\_ST bit assignments

![mhus.pbx_pdbcw_n__int_st bit assignments](images/0126-PDBCW-n-_INT_ST-Postbox-Doorbell-Channel-Window-n-Interrupt-Status-Register-n-0-127-img01.svg)

<table id="mhus_pbx_pdbcw_n__int_st__apdbcwn_int_st-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PDBCW&lt;n&gt;_INT_ST bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d53558e157" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53558e160" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53558e163" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d53558e166" rowspan="1">
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
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    TFR_ACK
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No Transfer Acknowledge event
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Transfer Acknowledge event
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d53558e274" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53558e277" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53558e280" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d53558e283" rowspan="1">
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
    (32 * n) + 0x1010
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PDBCW&lt;n&gt;_INT_ST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
