# FMU_PIDR4, MHU FMU Peripheral ID 4 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-PIDR4--MHU-FMU-Peripheral-ID-4-Register>

### FMU\_PIDR4, MHU FMU Peripheral ID 4 Register

Returns byte[4] of the peripheral ID for MHU FMU page.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHU FMU Register Block

Register offset
:   0xFD0

### Bit descriptions

Figure 1. MHU\_FMU\_REGISTER\_BLOCK\_FMU\_PIDR4 bit assignments

![mhu_fmu_register_block_fmu_pidr4 bit assignments](images/0064-FMU_PIDR4-MHU-FMU-Peripheral-ID-4-Register-img01.svg)

<table id="mhu_fmu_register_block_fmu_pidr4__afmu_pidr4-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   FMU_PIDR4 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d18097e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18097e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18097e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d18097e160" rowspan="1">
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
    SIZE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Size of the component
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       The size of the component must be identified using a combination of the following registers:
      </p>
      <ul>
       <li>
        <p>
         Peripheral ID 0-7 registers
        </p>
       </li>
       <li>
        <p>
         Component ID 0-3 registers
        </p>
       </li>
       <li>
        <p>
         &lt;x&gt;_FEAT_SPT0 and &lt;x&gt;_FEAT_SPT1 registers
        </p>
       </li>
      </ul>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    DES_2
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     JEP106 continuation code
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0100
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
   <th class="documents-nocellnorowborder" colspan="1" id="d18097e310" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18097e313" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18097e316" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d18097e319" rowspan="1">
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
    0xFD0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FMU_PIDR4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
