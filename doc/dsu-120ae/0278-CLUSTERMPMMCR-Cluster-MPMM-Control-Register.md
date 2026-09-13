# CLUSTERMPMMCR, Cluster MPMM Control Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERMPMMCR--Cluster-MPMM-Control-Register>

### CLUSTERMPMMCR, Cluster MPMM Control Register

Provides controls to enable/disable MPMM and configure the MPMM gears.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   Cluster

Register offset
:   0x0088

Access type
:   RW

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_clustermpmmcr bit assignments

![ext_clustermpmmcr bit assignments](images/0278-CLUSTERMPMMCR-Cluster-MPMM-Control-Register-img01.svg)

<table id="oqx1733414927257__aclustermpmmcr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERMPMMCR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d139907e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d139907e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d139907e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d139907e146" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="oqx1733414927257__63-4-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3:1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MPMMGEAR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MPMM Gear select.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="oqx1733414927257__id-3-1-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPMMEN
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Enable MPMM.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       MPMM disabled
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       MPMM enabled
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="oqx1733414927257__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d139907e275" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d139907e278" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d139907e281" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d139907e284" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Cluster
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0088
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERMPMMCR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
