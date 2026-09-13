# CLUSTERPMU_PMCEID2, Cluster Performance Monitors Common Event Identification register 2

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID2--Cluster-Performance-Monitors-Common-Event-Identification-register-2>

### CLUSTERPMU\_PMCEID2, Cluster Performance Monitors Common Event Identification register 2

Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the range 0x4000 to 0x401F.

When the value of a bit in the register is 1 the corresponding common event is implemented and counted.

### Configurations

External register CLUSTERPMU\_PMCEID2 bits [31:0] are architecturally mapped to AArch64 System register [IMP\_CLUSTERPMCEID0\_EL1, Performance Monitors Common Event Identification Register 0](/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCEID0-EL1--Performance-Monitors-Common-Event-Identification-Register-0?lang=en "Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the ranges 0x0000 to 0x001F and 0x4000 to 0x401F.") bits [63:32].

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xE28

Access type
:   See bit descriptions

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_clusterpmu\_pmceid2 bit assignments

![ext_clusterpmu_pmceid2 bit assignments](images/0611-CLUSTERPMU_PMCEID2-Cluster-Performance-Monitors-Common-Event-Identification-register-2-img01.svg)

<table id="jeb1733415324730__aclusterpmu_pmceid2-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMCEID2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d313503e153" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d313503e156" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d313503e159" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d313503e162" rowspan="1">
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
    IDhi31
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x401F
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
       Event 0x401F not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-31-reset" rowspan="1">
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
    IDhi30
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x401E
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
       Event 0x401E not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-30-reset" rowspan="1">
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
    IDhi29
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x401D
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
       Event 0x401D not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-29-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    IDhi28
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x401C
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
       Event 0x401C not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-28-reset" rowspan="1">
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
    IDhi27
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x401B
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
       Event 0x401B not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-27-reset" rowspan="1">
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
    IDhi26
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x401A
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
       Event 0x401A not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-26-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [25]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    IDhi25
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4019
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
       Event 0x4019 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-25-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    IDhi24
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4018
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
       Event 0x4018 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-24-reset" rowspan="1">
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
    IDhi23
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4017
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
       Event 0x4017 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-23-reset" rowspan="1">
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
    IDhi22
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4016
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
       Event 0x4016 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-22-reset" rowspan="1">
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
    IDhi21
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4015
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
       Event 0x4015 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-21-reset" rowspan="1">
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
    IDhi20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4014
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
       Event 0x4014 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-20-reset" rowspan="1">
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
    IDhi19
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4013
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
       Event 0x4013 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-19-reset" rowspan="1">
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
    IDhi18
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4012
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
       Event 0x4012 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-18-reset" rowspan="1">
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
    IDhi17
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4011
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
       Event 0x4011 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-17-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    IDhi16
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4010
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
       Event 0x4010 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-16-reset" rowspan="1">
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
    IDhi15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x400F
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
       Event 0x400F not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-15-reset" rowspan="1">
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
    IDhi14
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x400E
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
       Event 0x400E not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-14-reset" rowspan="1">
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
    IDhi13
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x400D
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
       Event 0x400D not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-13-reset" rowspan="1">
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
    IDhi12
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x400C
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
       Event 0x400C not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-12-reset" rowspan="1">
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
    IDhi11
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x400B
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
       Event 0x400B not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-11-reset" rowspan="1">
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
    IDhi10
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x400A
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
       Event 0x400A not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-10-reset" rowspan="1">
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
    IDhi9
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4009
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
       Event 0x4009 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-9-reset" rowspan="1">
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
    IDhi8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4008
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
       Event 0x4008 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-8-reset" rowspan="1">
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
    IDhi7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4007
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
       Event 0x4007 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-7-reset" rowspan="1">
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
    IDhi6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4006
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
       Event 0x4006 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-6-reset" rowspan="1">
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
    IDhi5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4005
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
       Event 0x4005 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-5-reset" rowspan="1">
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
    IDhi4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4004
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
       Event 0x4004 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-4-reset" rowspan="1">
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
    IDhi3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4003
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
       Event 0x4003 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-3-reset" rowspan="1">
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
    IDhi2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4002
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
       Event 0x4002 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-2-reset" rowspan="1">
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
    IDhi1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4001
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
       Event 0x4001 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jeb1733415324730__id-1-reset" rowspan="1">
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
    IDhi0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x4000
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
       Event 0x4000 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="jeb1733415324730__id-0-reset" rowspan="1">
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
