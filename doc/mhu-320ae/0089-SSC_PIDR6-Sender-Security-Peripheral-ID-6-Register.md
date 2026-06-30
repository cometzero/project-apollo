# SSC_PIDR6, Sender Security Peripheral ID 6 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Security-Control-register-summary/SSC-PIDR6--Sender-Security-Peripheral-ID-6-Register>

### SSC\_PIDR6, Sender Security Peripheral ID 6 Register

Returns byte[6] of the peripheral ID for Sender Security page.

### Configurations

This register is present only when TZE is implemented for the MHUS. Otherwise, direct accesses to SSC\_PIDR6 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.SSC

Register offset
:   0x0FD8

### Bit descriptions

Figure 1. MHUS.SSC\_SSC\_PIDR6 bit assignments

![mhus.ssc_ssc_pidr6 bit assignments](images/0089-SSC_PIDR6-Sender-Security-Peripheral-ID-6-Register-img01.svg)

<table id="mhus_ssc_ssc_pidr6__assc_pidr6-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SSC_PIDR6 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d114222e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d114222e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d114222e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d114222e163" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d114222e220" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d114222e223" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d114222e226" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d114222e229" rowspan="1">
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
    0x0FD8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SSC_PIDR6
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
