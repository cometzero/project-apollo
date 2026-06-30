# MDBCW<n>_MSK_CLR, Mailbox Doorbell Channel Window <n> Mask Clear Register, n = 0 - 127

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MDBCW-n--MSK-CLR--Mailbox-Doorbell-Channel-Window--n--Mask-Clear-Register--n---0---127>

### MDBCW<n>\_MSK\_CLR, Mailbox Doorbell Channel Window <n> Mask Clear Register, n = 0 - 127

Allows clearing doorbell channel mask

### Configurations

This register is present only when DBE is implemented. Otherwise, direct accesses to MDBCW<n>\_MSK\_CLR are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   (32 \* n) + 0x1018

### Bit descriptions

Figure 1. MHUR.MBX\_MDBCW<n>\_MSK\_CLR bit assignments

![mhur.mbx_mdbcw_n__msk_clr bit assignments](images/0227-MDBCW-n-_MSK_CLR-Mailbox-Doorbell-Channel-Window-n-Mask-Clear-Register-n-0-127-img01.svg)

<table id="mhur_mbx_mdbcw_n__msk_clr__amdbcwn_msk_clr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MDBCW&lt;n&gt;_MSK_CLR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d121081e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d121081e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d121081e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d121081e163" rowspan="1">
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
    MSK&lt;x&gt;
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Writes of 1 cause the associated bit in the MDBCW&lt;n&gt;_MSK_ST registers to be set to 0. Writing 0 has no effect on the value of MDBCW&lt;n&gt;_MSK_ST.
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
       Set associated bit in MDBCW&lt;n&gt;_MSK_ST register to 0
      </p>
     </dd>
    </dl>
    <p>
     Field always reads as 0
    </p>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d121081e256" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d121081e259" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d121081e262" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d121081e265" rowspan="1">
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
    (32 * n) + 0x1018
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MDBCW&lt;n&gt;_MSK_CLR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
