# CLUSTERL3UPTH2, Cluster L3 Upsize Threshold2 Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERL3UPTH2--Cluster-L3-Upsize-Threshold2-Register>

### CLUSTERL3UPTH2, Cluster L3 Upsize Threshold2 Register

This register is intended for use in algorithms for determining when to power up slices.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   Cluster

Register offset
:   0x0090

Access type
:   RW

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_clusterl3upth2 bit assignments

![ext_clusterl3upth2 bit assignments](images/0279-CLUSTERL3UPTH2-Cluster-L3-Upsize-Threshold2-Register-img01.svg)

<table id="uiz1733414869724__aclusterl3upth2-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERL3UPTH2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d111749e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111749e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111749e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d111749e146" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="uiz1733414869724__63-32-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [31:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    UPTH2
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     If all the L3 ways are powered, but not all of the slices are powered, and the cache miss bandwidth rises above this threshold then the number of slices is upsized. The value in this register is compared with the change in the cluster L3 miss counter since the last time period.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="uiz1733414869724__id-31-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000
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
   <th class="documents-nocellnorowborder" colspan="1" id="d111749e221" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111749e224" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111749e227" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d111749e230" rowspan="1">
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
    0x0090
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERL3UPTH2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
