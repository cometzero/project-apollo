# FMU_TIMEOUT, FMU Timeout Duration Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-TIMEOUT--FMU-Timeout-Duration-Register>

### FMU\_TIMEOUT, FMU Timeout Duration Register

Defines the duration of the timeout period before TIMEOUT is reported in FMU\_STATUS

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHU FMU Register Block

Register offset
:   0xF24

### Bit descriptions

Figure 1. MHU\_FMU\_REGISTER\_BLOCK\_FMU\_TIMEOUT bit assignments

![mhu_fmu_register_block_fmu_timeout bit assignments](images/0059-FMU_TIMEOUT-FMU-Timeout-Duration-Register-img01.svg)

<table id="mhu_fmu_register_block_fmu_timeout__afmu_timeout-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   FMU_TIMEOUT bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d113134e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d113134e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d113134e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d113134e160" rowspan="1">
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
    DURATION
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Timeout count duration in clock cycles. The initial value on reset is all 1s to indicate the longest possible timeout allowed.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xFFFFFFFF
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
   <th class="documents-nocellnorowborder" colspan="1" id="d113134e217" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d113134e220" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d113134e223" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d113134e226" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHU FMU Register Block
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xF24
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FMU_TIMEOUT
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
