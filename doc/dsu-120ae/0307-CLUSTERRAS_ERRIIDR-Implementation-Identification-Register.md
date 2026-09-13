# CLUSTERRAS_ERRIIDR, Implementation Identification Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRIIDR--Implementation-Identification-Register>

### CLUSTERRAS\_ERRIIDR, Implementation Identification Register

Defines the implementer of the product.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERRAS

Register offset
:   0xE10

Access type
:   RO

Reset value
:   0100 1110 1100 0000 0001 0100 0011 1011

### Bit descriptions

Figure 1. ext\_clusterras\_erriidr bit assignments

![ext_clusterras_erriidr bit assignments](images/0307-CLUSTERRAS_ERRIIDR-Implementation-Identification-Register-img01.svg)

<table id="pfu1733414946467__aclusterras_erriidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERRIIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d7176e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7176e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7176e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d7176e146" rowspan="1">
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
     Part number, bits [11:0]. The part number is selected by the designer of the product.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010011101100
      </span>
     </dt>
     <dd>
      <p>
       DSU-120AE Cluster RAS.
      </p>
     </dd>
    </dl>
    <p>
     ext-CLUSTERRAS_ERRPIDR0.PART_0 matches bits [7:0] of CLUSTERRAS_ERRIIDR.ProductID and ext-CLUSTERRAS_ERRPIDR1.PART_1 matches bits [11:8] of CLUSTERRAS_ERRIIDR.ProductID.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pfu1733414946467__id-31-20-reset" rowspan="1">
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
     Product major revision.
    </p>
    <p>
     This field distinguishes product variants or major revisions of the product.
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
    <p>
     ext-CLUSTERRAS_ERRPIDR2.REVISION matches CLUSTERRAS_ERRIIDR.Variant.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pfu1733414946467__id-19-16-reset" rowspan="1">
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
     Product minor revision.
    </p>
    <p>
     This field distinguishes minor revisions of the product.
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
    <p>
     ext-CLUSTERRAS_ERRPIDR3.REVAND matches CLUSTERRAS_ERRIIDR.Revision.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pfu1733414946467__id-15-12-reset" rowspan="1">
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
      <p>
       JEP106 ID code for Arm Limited.
      </p>
     </dd>
    </dl>
    <p>
     Bits [11:8] contain the JEP106 continuation code of the implementer, and bits [6:0] contain the JEP106 identity code of the implementer. Bit 7 is
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     ext-CLUSTERRAS_ERRPIDR4.DES_2 matches bits [11:8] of CLUSTERRAS_ERRIIDR.Implementer, ext-CLUSTERRAS_ERRPIDR2.DES_1 matches bits [6:4] of CLUSTERRAS_ERRIIDR.Implementer, and ext-CLUSTERRAS_ERRPIDR1.DES_0 matches bits [3:0] of CLUSTERRAS_ERRIIDR.Implementer.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="pfu1733414946467__id-11-0-reset" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d7176e330" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7176e333" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7176e336" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d7176e339" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xE10
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERRIIDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
