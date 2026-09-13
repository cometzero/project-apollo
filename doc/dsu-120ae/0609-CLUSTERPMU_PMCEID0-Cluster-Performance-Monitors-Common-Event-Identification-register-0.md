# CLUSTERPMU_PMCEID0, Cluster Performance Monitors Common Event Identification register 0

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID0--Cluster-Performance-Monitors-Common-Event-Identification-register-0>

### CLUSTERPMU\_PMCEID0, Cluster Performance Monitors Common Event Identification register 0

Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the range 0x0000 to 0x001F

When the value of a bit in the register is 1 the corresponding common event is implemented and counted.

### Configurations

External register CLUSTERPMU\_PMCEID0 bits [31:0] are architecturally mapped to AArch64 System register [IMP\_CLUSTERPMCEID0\_EL1, Performance Monitors Common Event Identification Register 0](/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCEID0-EL1--Performance-Monitors-Common-Event-Identification-Register-0?lang=en "Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the ranges 0x0000 to 0x001F and 0x4000 to 0x401F.") bits [31:0].

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xE20

Access type
:   See bit descriptions

Reset value
:   0010 0110 0000 0010 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_clusterpmu\_pmceid0 bit assignments

![ext_clusterpmu_pmceid0 bit assignments](images/0609-CLUSTERPMU_PMCEID0-Cluster-Performance-Monitors-Common-Event-Identification-register-0-img01.svg)

<table id="qoq1733415319725__aclusterpmu_pmceid0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMCEID0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d252379e153" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d252379e156" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d252379e159" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d252379e162" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID31
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x001F
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x001F not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-31-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID30
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x001E
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       CHAIN event not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-30-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [29]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID29
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x001D
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       BUS_CYCLES event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-29-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID28
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x001C
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x001C not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-28-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID27
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x001B
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x001B not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-27-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [26]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID26
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x001A
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       MEMORY_ERROR event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-26-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [25]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID25
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0019
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       BUS_ACCESS event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-25-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID24
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0018
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0018 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-24-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID23
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0017
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0017 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-23-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [22]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID22
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0016
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0016 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-22-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [21]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID21
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0015
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0015 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-21-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0014
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0014 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-20-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID19
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0013
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0013 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-19-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [18]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID18
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0012
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0012 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-18-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [17]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID17
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0011
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       CYCLES event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-17-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID16
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0010
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0010 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x000F
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x000F not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-15-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [14]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID14
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x000E
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x000E not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-14-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [13]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID13
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x000D
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x000D not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-13-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID12
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x000C
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x000C not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-12-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID11
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x000B
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x000B not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-11-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID10
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x000A
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x000A not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-10-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID9
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0009
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0009 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-9-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0008
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0008 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0007
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0007 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-7-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0006
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0006 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-6-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0005
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0005 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-5-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0004
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0004 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0003
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0003 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0002
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0002 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0001
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0001 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="qoq1733415319725__id-1-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ID0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0000
     </span>
     implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Event 0x0000 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="qoq1733415319725__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

When IsCorePowered() && !DoubleLockStatus() && !OSLockStatus() && AllowExternalPMUAccess()
:   RO

Otherwise
:   ERROR
