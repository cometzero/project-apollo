# CLUSTERPMU_PMIIDR, Cluster Performance Monitors Implementation Identification register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMIIDR--Cluster-Performance-Monitors-Implementation-Identification-register>

### CLUSTERPMU\_PMIIDR, Cluster Performance Monitors Implementation Identification register

Defines the implemented of the component..

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xE08

Access type
:   See bit descriptions

Reset value
:   0100 1110 1100 0000 0001 0100 0011 1011

### Bit descriptions

Figure 1. ext\_clusterpmu\_pmiidr bit assignments

![ext_clusterpmu_pmiidr bit assignments](images/0608-CLUSTERPMU_PMIIDR-Cluster-Performance-Monitors-Implementation-Identification-register-img01.svg)

<table id="hkf1733415317330__aclusterpmu_pmiidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMIIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d66572e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d66572e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d66572e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d66572e146" rowspan="1">
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
     Value identifying the PMU Component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010011101100
      </span>
     </dt>
     <dd>
      <p>
       DSU-120AE Cluster PMU.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hkf1733415317330__id-31-20-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="hkf1733415317330__id-19-16-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="hkf1733415317330__id-15-12-reset" rowspan="1">
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
     Contains the JEP106 code of the company that implemented the PMU Component.
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
   <td class="documents-cellrowborder" colspan="1" id="hkf1733415317330__id-11-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x43B
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

When IsCorePowered()
:   RO

Otherwise
:   ERROR
