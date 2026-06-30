# RRAS_ERRIIDR, Implementation Identification Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERRIIDR--Implementation-Identification-Register>

### RRAS\_ERRIIDR, Implementation Identification Register

Defines the implementer of the component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHUR.RRAS

Register offset
:   0x0E10

### Bit descriptions

Figure 1. MHUR\_RRAS\_ERRIIDR bit assignments

![mhur_rras_erriidr bit assignments](images/0257-RRAS_ERRIIDR-Implementation-Identification-Register-img01.svg)

<table id="mhur_rras_erriidr__arras_erriidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RRAS_ERRIIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d22463e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d22463e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d22463e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d22463e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ProductID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Part number, bits [11:0]. The part number is selected by the designer of the component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000011110111
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0F7
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Variant
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Component major revision. This field distinguishes product variants or major revisions of the product.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The reset value depends on the product version used.
    <ul>
     <li>
      <span class="documents-g.number.hex">
       0x0
      </span>
      - r0
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Revision
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Component minor revision. This field distinguishes minor revisions of the product.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The reset value depends on the product version used.
    <ul>
     <li>
      <span class="documents-g.number.hex">
       0x0
      </span>
      - p0
     </li>
     <li>
      <span class="documents-g.number.hex">
       0x1
      </span>
      - p1
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [11:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Implementer
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Contains the JEP106 code of the company that implemented the RAS component. For an Arm implementation, this field has the value
     <span class="documents-g.number.hex">
      0x43B
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010000111011
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x43B
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
   <th class="documents-nocellnorowborder" colspan="1" id="d22463e326" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d22463e329" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d22463e332" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d22463e335" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.RRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0E10
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RRAS_ERRIIDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
