# FMU_CIDR0, MHU FMU Component ID 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-CIDR0--MHU-FMU-Component-ID-0-Register>

### FMU\_CIDR0, MHU FMU Component ID 0 Register

Returns byte[0] of the component ID for MHU FMU page.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHU FMU Register Block

Register offset
:   0xFF0

### Bit descriptions

Figure 1. MHU\_FMU\_REGISTER\_BLOCK\_FMU\_CIDR0 bit assignments

![mhu_fmu_register_block_fmu_cidr0 bit assignments](images/0072-FMU_CIDR0-MHU-FMU-Component-ID-0-Register-img01.svg)

<table id="mhu_fmu_register_block_fmu_cidr0__afmu_cidr0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   FMU_CIDR0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d131183e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d131183e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d131183e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d131183e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:8]
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
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PRMBL_0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Preamble, segment 0
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001101
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0D
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
   <th class="documents-nocellnorowborder" colspan="1" id="d131183e252" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d131183e255" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d131183e258" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d131183e261" rowspan="1">
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
    0xFF0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FMU_CIDR0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
