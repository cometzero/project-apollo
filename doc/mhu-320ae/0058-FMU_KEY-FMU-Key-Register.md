# FMU_KEY, FMU Key Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-FMU-register-summary/FMU-KEY--FMU-Key-Register>

### FMU\_KEY, FMU Key Register

Used to receiver the unlock key that is required for writes to FMU registers to be successful. This mechanism does not affect ability to perform FMU reads.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHU FMU Register Block

Register offset
:   0xF20

### Bit descriptions

Figure 1. MHU\_FMU\_REGISTER\_BLOCK\_FMU\_KEY bit assignments

![mhu_fmu_register_block_fmu_key bit assignments](images/0058-FMU_KEY-FMU-Key-Register-img01.svg)

<table id="mhu_fmu_register_block_fmu_key__afmu_key-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   FMU_KEY bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d83722e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d83722e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d83722e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d83722e160" rowspan="1">
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
    KEY
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Writing the correct key to this field enables the next write to any other writable FMU register to succeed.
    </p>
    <p>
     The register file is unlocked when a write to FMU_KEY occurs that satisfies all of the following conditions:
    </p>
    <ul>
     <li>
      <p>
       Is Secure
      </p>
     </li>
     <li>
      <p>
       Is for 32 bits
      </p>
     </li>
     <li>
      <p>
       The bottom 8 bits are
       <span class="documents-g.number.hex">
        0xBE
       </span>
      </p>
     </li>
    </ul>
    <p>
     If the register file is unlocked, the FMU_KEY register reads as
     <span class="documents-g.number.hex">
      0x00000BE
     </span>
     . Otherwise, the FMU_KEY register reads as
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
    <p>
     The FMU_KEY register automatically locks after most Secure write access. The FMU_KEY register locks even if the Secure write is ignored, for example, if it is a write to invalid address. However, the FMU_KEY does not lock automatically for Secure writes to the upper 32-bits of the 64-bit RAS registers FMU_ERR&lt;n&gt;CTLR and FMU_ERR&lt;n&gt;STATUS.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
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
   <th class="documents-nocellnorowborder" colspan="1" id="d83722e273" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d83722e276" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d83722e279" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d83722e282" rowspan="1">
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
    0xF20
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FMU_KEY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
