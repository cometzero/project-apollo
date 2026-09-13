# MPAMF_IIDR, MPAM Implementation Identification Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-IIDR--MPAM-Implementation-Identification-Register>

### MPAMF\_IIDR, MPAM Implementation Identification Register

Uniquely identifies the MSC implementation by the combination of implementer, product ID, variant and revision.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offsets (2)
:   0x0018,0x0018

Access type
:   RO

Reset value
:   0100 1110 1100 0000 0001 0100 0011 1011

### Bit descriptions

Figure 1. ext\_mpamf\_iidr bit assignments

![ext_mpamf_iidr bit assignments](images/0283-MPAMF_IIDR-MPAM-Implementation-Identification-Register-img01.svg)

<table id="kvh1733414931684__ampamf_iidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMF_IIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d10972e146" rowspan="1">
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
     Value identifying the MPAM Memory System Component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010011101100
      </span>
     </dt>
     <dd>
      <p>
       DSU-120AE Cluster MPAM.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="kvh1733414931684__id-31-20-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x4EC
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
     Value used to distinguish product variants, or major revisions of the product.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Product variant 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="kvh1733414931684__id-19-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
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
     Value used to distinguish minor revisions of the product.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Product revision 0.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Product revision 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="kvh1733414931684__id-15-12-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
    </span>
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
     Contains the JEP106 code of the company that implemented the MPAM Memory System Component.
    </p>
    <p>
     For an Arm implementation, bits[11:0] are
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
      <p>
       Arm implementation.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="kvh1733414931684__id-11-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x43B
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e344" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e347" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e350" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d10972e353" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0018
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_IIDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e401" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e404" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10972e407" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d10972e410" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0018
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_IIDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
