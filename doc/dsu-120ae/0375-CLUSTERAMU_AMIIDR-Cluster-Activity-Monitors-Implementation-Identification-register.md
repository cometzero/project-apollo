# CLUSTERAMU_AMIIDR, Cluster Activity Monitors Implementation Identification register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMIIDR--Cluster-Activity-Monitors-Implementation-Identification-register>

### CLUSTERAMU\_AMIIDR, Cluster Activity Monitors Implementation Identification register

Defines the implemented of the component..

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERAMU

Register offset
:   0xE08

Access type
:   RO

Reset value
:   0100 1110 1100 0000 0001 0100 0011 1011

### Bit descriptions

Figure 1. ext\_clusteramu\_amiidr bit assignments

![ext_clusteramu_amiidr bit assignments](images/0375-CLUSTERAMU_AMIIDR-Cluster-Activity-Monitors-Implementation-Identification-register-img01.svg)

<table id="sql1733415017973__aclusteramu_amiidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMIIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d44438e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d44438e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d44438e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d44438e146" rowspan="1">
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
     Value identifying the AMU Component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010011101100
      </span>
     </dt>
     <dd>
      <p>
       DSU-120AE Cluster AMU.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sql1733415017973__id-31-20-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="sql1733415017973__id-19-16-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="sql1733415017973__id-15-12-reset" rowspan="1">
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
     Contains the JEP106 code of the company that implemented the AMU Component.
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
   <td class="documents-cellrowborder" colspan="1" id="sql1733415017973__id-11-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x43B
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
