# CLUSTERCFR2, Cluster Configuration Register 2

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERCFR2--Cluster-Configuration-Register-2>

### CLUSTERCFR2, Cluster Configuration Register 2

Contains details of the hardware configuration of the cluster.

### Configurations

External register CLUSTERCFR2 bits [63:0] are architecturally mapped to AArch64 System register [IMP\_CLUSTERCFR2\_EL1, Cluster Configuration Register 2](/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCFR2-EL1--Cluster-Configuration-Register-2?lang=en "Contains details of the hardware configuration of the cluster.") bits [63:0].

### Attributes

Width
:   64

Component
:   Cluster

Register offset
:   0x0068

Access type
:   RO

Reset value
:   ```
    0000 0000 0000 0000 0000 00xx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clustercfr2 bit assignments

![ext_clustercfr2 bit assignments](images/0276-CLUSTERCFR2-Cluster-Configuration-Register-2-img01.svg)

<table id="mmg1733414867554__aclustercfr2-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERCFR2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d334314e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d334314e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d334314e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d334314e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:42]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mmg1733414867554__63-42-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [41:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CRS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Core register slices. Each three bits represents a core, with [2:0] for core 0 up to [41:39] for core 13.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000000
      </span>
     </dt>
     <dd>
      <p>
       No register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000001
      </span>
     </dt>
     <dd>
      <p>
       One register slice
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000010
      </span>
     </dt>
     <dd>
      <p>
       Two register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000011
      </span>
     </dt>
     <dd>
      <p>
       Three register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000100
      </span>
     </dt>
     <dd>
      <p>
       Four register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000101
      </span>
     </dt>
     <dd>
      <p>
       Five register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000110
      </span>
     </dt>
     <dd>
      <p>
       Six register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000111
      </span>
     </dt>
     <dd>
      <p>
       Seven register slices
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="mmg1733414867554__id-41-0-reset" rowspan="1">
    <code>
     42{x}
    </code>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d334314e359" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d334314e362" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d334314e365" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d334314e368" rowspan="1">
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
    0x0068
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERCFR2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
