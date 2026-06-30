# SSC_IIDR, Sender Security Implementer Identification Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Security-Control-register-summary/SSC-IIDR--Sender-Security-Implementer-Identification-Register>

### SSC\_IIDR, Sender Security Implementer Identification Register

This field provides information on the Implementer of the MHU

### Configurations

This register is present only when TZE is implemented for the MHUS. Otherwise, direct accesses to SSC\_IIDR are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.SSC

Register offset
:   0x0FC8

### Bit descriptions

Figure 1. MHUS.SSC\_SSC\_IIDR bit assignments

![mhus.ssc_ssc_iidr bit assignments](images/0085-SSC_IIDR-Sender-Security-Implementer-Identification-Register-img01.svg)

<table id="mhus_ssc_ssc_iidr__assc_iidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SSC_IIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d98917e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d98917e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d98917e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d98917e163" rowspan="1">
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
    PRODUCT_ID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Product ID of the MHU implementation
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
    VARIANT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Variant or Major revision of the MHU implementation
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
    REVISION
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Revision or minor version of the MHU implementation
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
    IMPLEMENTER
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Implementer ID
    </p>
    <p>
     Contains the JEP106 identification information as follows:
    </p>
    <ul>
     <li>
      <p>
       11:8 - JEP106 continuation code of implementer
      </p>
     </li>
     <li>
      <p>
       7 - Always 0
      </p>
     </li>
     <li>
      <p>
       6:0 - JEP106 identity code of implementer
      </p>
     </li>
    </ul>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d98917e340" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d98917e343" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d98917e346" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d98917e349" rowspan="1">
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
    0x0FC8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SSC_IIDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
