# RRAS_ERR<n>MISC3, Error Record <n> Miscellaneous Register 3, n = 0 - 9

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-MISC3--Error-Record--n--Miscellaneous-Register-3--n---0---9>

### RRAS\_ERR<n>MISC3, Error Record <n> Miscellaneous Register 3, n = 0 - 9

Records additional information on reported error.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   MHUR.RRAS

Register offset
:   (64 \* n) + 0x0038

### Bit descriptions

Figure 1. MHUR\_RRAS\_ERR<n>MISC3 bit assignments

![mhur_rras_err_n_misc3 bit assignments](images/0255-RRAS_ERR-n-MISC3-Error-Record-n-Miscellaneous-Register-3-n-0-9-img01.svg)

<table id="hur_rras_err_n_misc3__arras_errnmisc3-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RRAS_ERR&lt;n&gt;MISC3 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d46800e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d46800e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d46800e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d46800e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [63:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d46800e217" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d46800e220" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d46800e223" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d46800e226" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.RRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    (64 * n) + 0x0038
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RRAS_ERR&lt;n&gt;MISC3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
