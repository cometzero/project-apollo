# CLUSTERL3DNTH1, Cluster L3 Downsize Threshold1 Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERL3DNTH1--Cluster-L3-Downsize-Threshold1-Register>

### CLUSTERL3DNTH1, Cluster L3 Downsize Threshold1 Register

This register is intended for use in algorithms for determining when to power up or down cache portions.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   Cluster

Register offset
:   0x0030

Access type
:   RW

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_clusterl3dnth1 bit assignments

![ext_clusterl3dnth1 bit assignments](images/0269-CLUSTERL3DNTH1-Cluster-L3-Downsize-Threshold1-Register-img01.svg)

<table id="iwa1733414854666__aclusterl3dnth1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERL3DNTH1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d29224e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d29224e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d29224e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d29224e146" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="iwa1733414854666__63-32-reset" rowspan="1">
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
    DNTH1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     If all L3 ways are powered and the cache hit bandwidth falls below this threshold then the cache is downsized to none the ways. The value in this register is compared with the change in the cluster L3 hit counter since the last time period.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="iwa1733414854666__id-31-0-reset" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d29224e221" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d29224e224" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d29224e227" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d29224e230" rowspan="1">
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
    0x0030
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERL3DNTH1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
