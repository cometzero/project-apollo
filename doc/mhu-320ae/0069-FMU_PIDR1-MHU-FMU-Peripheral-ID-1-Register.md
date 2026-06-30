# FMU_PIDR1, MHU FMU Peripheral ID 1 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR1--MHU-FMU-Peripheral-ID-1-Register>

### FMU\_PIDR1, MHU FMU Peripheral ID 1 Register

Returns byte[1] of the peripheral ID for MHU FMU page.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHU FMU Register Block

Register offset
:   0xFE4

### Bit descriptions

Figure 1. MHU\_FMU\_REGISTER\_BLOCK\_FMU\_PIDR1 bit assignments

![mhu_fmu_register_block_fmu_pidr1 bit assignments](images/0069-FMU_PIDR1-MHU-FMU-Peripheral-ID-1-Register-img01.svg)

<table id="mhu_fmu_register_block_fmu_pidr1__afmu_pidr1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   FMU_PIDR1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d66097e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d66097e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d66097e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d66097e160" rowspan="1">
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DES_0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Bits 3:0 of the JEP106 identification code
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1011
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1011
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PART_1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Bits 11:8 of the Part ID for the implementation of the MHU
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
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
   <th class="documents-nocellnorowborder" colspan="1" id="d66097e271" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d66097e274" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d66097e277" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d66097e280" rowspan="1">
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
    0xFE4
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FMU_PIDR1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
