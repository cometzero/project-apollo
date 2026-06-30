# FMU_PIDR0, MHU FMU Peripheral ID 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR0--MHU-FMU-Peripheral-ID-0-Register>

### FMU\_PIDR0, MHU FMU Peripheral ID 0 Register

Returns byte[0] of the peripheral ID for MHU FMU page.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHU FMU Register Block

Register offset
:   0xFE0

### Bit descriptions

Figure 1. MHU\_FMU\_REGISTER\_BLOCK\_FMU\_PIDR0 bit assignments

![mhu_fmu_register_block_fmu_pidr0 bit assignments](images/0068-FMU_PIDR0-MHU-FMU-Peripheral-ID-0-Register-img01.svg)

<table id="mhu_fmu_register_block_fmu_pidr0__afmu_pidr0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   FMU_PIDR0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d57060e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57060e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57060e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d57060e160" rowspan="1">
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
    PART_0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Bits 7:0 of the Part ID for the implementation of the MHU
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The reset value depends on whether the FMU is located in the MHU Sender or MHU Receiver.
    <ul id="mhu_fmu_register_block_fmu_pidr0__ul_odx_vlb_tzb">
     <li>
      <span class="documents-g.number.hex">
       0x9C
      </span>
      - MHU Sender FMU
     </li>
     <li>
      <span class="documents-g.number.hex">
       0x9D
      </span>
      - MHU Receiver FMU
     </li>
    </ul>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d57060e248" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57060e251" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57060e254" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d57060e257" rowspan="1">
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
    0xFE0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FMU_PIDR0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
