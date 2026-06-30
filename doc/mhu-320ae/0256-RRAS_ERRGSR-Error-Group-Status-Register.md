# RRAS_ERRGSR, Error Group Status Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERRGSR--Error-Group-Status-Register>

### RRAS\_ERRGSR, Error Group Status Register

Shows the status for the records in the group.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   MHUR.RRAS

Register offset
:   0x0E00

### Bit descriptions

Figure 1. MHUR\_RRAS\_ERRGSR bit assignments

![mhur_rras_errgsr bit assignments](images/0256-RRAS_ERRGSR-Error-Group-Status-Register-img01.svg)

<table id="mhur_rras_errgsr__arras_errgsr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RRAS_ERRGSR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d75591e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d75591e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d75591e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d75591e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:56]
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
    [55:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    S&lt;m&gt;, bit[m], where m = 55 to 0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     The status for error record &lt;m&gt;. A read-only copy of RRAS_ERR&lt;m&gt;STATUS.V.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       One or more errors.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000000000
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
   <th class="documents-nocellnorowborder" colspan="1" id="d75591e271" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d75591e274" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d75591e277" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d75591e280" rowspan="1">
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
    0x0E00
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RRAS_ERRGSR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
