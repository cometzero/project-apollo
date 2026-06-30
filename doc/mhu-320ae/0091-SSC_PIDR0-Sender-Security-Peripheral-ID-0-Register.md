# SSC_PIDR0, Sender Security Peripheral ID 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Security-Control-register-summary/SSC-PIDR0--Sender-Security-Peripheral-ID-0-Register>

### SSC\_PIDR0, Sender Security Peripheral ID 0 Register

Returns byte[0] of the peripheral ID for Sender Security page.

### Configurations

This register is present only when TZE is implemented for the MHUS. Otherwise, direct accesses to SSC\_PIDR0 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.SSC

Register offset
:   0x0FE0

### Bit descriptions

Figure 1. MHUS.SSC\_SSC\_PIDR0 bit assignments

![mhus.ssc_ssc_pidr0 bit assignments](images/0091-SSC_PIDR0-Sender-Security-Peripheral-ID-0-Register-img01.svg)

<table id="mhus_ssc_ssc_pidr0__assc_pidr0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SSC_PIDR0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d7006e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7006e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7006e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d7006e163" rowspan="1">
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
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11110111
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xF7
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
   <th class="documents-nocellnorowborder" colspan="1" id="d7006e255" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7006e258" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7006e261" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d7006e264" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUS.SSC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0FE0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SSC_PIDR0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
