# RSC_CIDR1, Receiver Security Component ID 1 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Security-Control-register-summary/RSC-CIDR1--Receiver-Security-Component-ID-1-Register>

### RSC\_CIDR1, Receiver Security Component ID 1 Register

Returns byte[1] of the component ID for Receiver Security page.

### Configurations

This register is present only when TZE is implemented for the MHUR. Otherwise, direct accesses to RSC\_CIDR1 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.RSC

Register offset
:   0x0FF4

### Bit descriptions

Figure 1. MHUR.RSC\_RSC\_CIDR1 bit assignments

![mhur.rsc_rsc_cidr1 bit assignments](images/0190-RSC_CIDR1-Receiver-Security-Component-ID-1-Register-img01.svg)

<table id="mhur_rsc_rsc_cidr1__arsc_cidr1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RSC_CIDR1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d97343e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d97343e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d97343e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d97343e163" rowspan="1">
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
    CLASS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Component Class
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1111
      </span>
     </dt>
     <dd>
      <p>
       CoreLink, PrimeCell, or system component with no standardized register layout, for backwards compatibility.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1111
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PRMBL_1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Preamble, segment 1
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
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
   <th class="documents-nocellnorowborder" colspan="1" id="d97343e294" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d97343e297" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d97343e300" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d97343e303" rowspan="1">
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
    0x0FF4
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RSC_CIDR1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
