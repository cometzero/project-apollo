# RSC_CIDR0, Receiver Security Component ID 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Security-Control-register-summary/RSC-CIDR0--Receiver-Security-Component-ID-0-Register>

### RSC\_CIDR0, Receiver Security Component ID 0 Register

Returns byte[0] of the component ID for Receiver Security page.

### Configurations

This register is present only when TZE is implemented for the MHUR. Otherwise, direct accesses to RSC\_CIDR0 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.RSC

Register offset
:   0x0FF0

### Bit descriptions

Figure 1. MHUR.RSC\_RSC\_CIDR0 bit assignments

![mhur.rsc_rsc_cidr0 bit assignments](images/0189-RSC_CIDR0-Receiver-Security-Component-ID-0-Register-img01.svg)

<table id="mhur_rsc_rsc_cidr0__arsc_cidr0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RSC_CIDR0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d52750e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d52750e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d52750e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d52750e163" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d52750e255" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d52750e258" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d52750e261" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d52750e264" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.RSC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0FF0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RSC_CIDR0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
