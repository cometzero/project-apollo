# IMP_CLUSTERPMCEID0_EL1, Performance Monitors Common Event Identification Register 0

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCEID0-EL1--Performance-Monitors-Common-Event-Identification-Register-0>

### IMP\_CLUSTERPMCEID0\_EL1, Performance Monitors Common Event Identification Register 0

Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the ranges 0x0000 to 0x001F and 0x4000 to 0x401F.

When the value of a bit in the register is 1 the corresponding common event is implemented and counted.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Functional group
:   Performance Monitors registers

Access type
:   See bit descriptions

Reset value
:   0000 0000 0000 0000 0001 1110 0000 0000 0010 0110 0000 0010 0000 0000 0000 0000

### Bit descriptions

Figure 1. AArch64\_imp\_clusterpmceid0\_el1 bit assignments

![AArch64_imp_clusterpmceid0_el1 bit assignments](images/0249-IMP_CLUSTERPMCEID0_EL1-Performance-Monitors-Common-Event-Identification-Register-0-img01.svg)

<table id="mst1733414890517__aimp_clusterpmceid0_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERPMCEID0_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e144" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e147" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e150" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d120628e153" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID63
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x003F
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
       Event 0x003F not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-63-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [62]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID62
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x003E
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
       Event 0x003E not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-62-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [61]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID61
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x003D
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
       Event 0x003D not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-61-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [60]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID60
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x003C
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
       Event 0x003C not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-60-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [59]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID59
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x003B
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
       Event 0x003B not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-59-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [58]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID58
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x003A
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
       Event 0x003A not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-58-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [57]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID57
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0039
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
       Event 0x0039 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-57-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [56]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID56
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0038
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
       Event 0x0038 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-56-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [55]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID55
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0037
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
       Event 0x0037 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-55-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [54]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID54
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0036
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
       Event 0x0036 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-54-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [53]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID53
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0035
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
       Event 0x0035 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-53-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [52]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID52
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0034
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
       Event 0x0034 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-52-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [51]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID51
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0033
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
       Event 0x0033 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-51-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [50]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID50
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0032
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
       Event 0x0032 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-50-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [49]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID49
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0031
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
       Event 0x0031 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-49-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [48]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID48
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0030
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
       Event 0x0030 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-48-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [47]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID47
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x002F
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
       Event 0x002F not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-47-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [46]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID46
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x002E
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
       Event 0x002E not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-46-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [45]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID45
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x002D
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
       Event 0x002D not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-45-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [44]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID44
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x002C
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
       L3D_CACHE_WB event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-44-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [43]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID43
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x002B
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
       L3D_CACHE event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-43-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [42]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID42
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x002A
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
       L3D_CACHE_REFILL event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-42-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [41]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID41
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0029
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
       L3D_CACHE_ALLOCATE event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-41-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [40]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID40
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0028
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
       Event 0x0028 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-40-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [39]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID39
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0027
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
       Event 0x0027 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-39-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [38]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID38
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0026
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
       Event 0x0026 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-38-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [37]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID37
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0025
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
       Event 0x0025 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-37-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [36]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID36
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0024
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
       Event 0x0024 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-36-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [35]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID35
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0023
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
       Event 0x0023 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-35-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [34]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID34
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0022
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
       Event 0x0022 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-34-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [33]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID33
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0021
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
       Event 0x0021 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-33-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ID32
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Common event
     <span class="documents-g.number.hex">
      0x0020
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
       Event 0x0020 not implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-32-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-31-reset" rowspan="1">
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
       CHAIN event implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-30-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-29-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-28-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-27-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-26-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-25-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-24-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-23-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-22-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-21-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-20-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-19-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-18-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-17-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-16-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-15-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-14-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-13-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-12-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-11-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-10-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-9-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-8-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-7-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-6-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-5-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-4-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-3-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-2-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mst1733414890517__id-1-reset" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="mst1733414890517__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C6\_4

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e2890" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e2893" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e2896" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e2899" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d120628e2902" rowspan="1">
    op2
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1111
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0110
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b100
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_0\_C15\_C6\_4, <Xt>

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e2967" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e2970" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e2973" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d120628e2976" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d120628e2979" rowspan="1">
    op2
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1111
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0110
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b100
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_0\_C15\_C6\_4

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERPMCEID0_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERPMCEID0_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERPMCEID0_EL1;
```

MSR S3\_0\_C15\_C6\_4, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && ACTLR_EL3.CLUSTERPMUEN == '0' then
        UNDEFINED;
    elsif EL2Enabled() && ACTLR_EL2.CLUSTERPMUEN == '0' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif ACTLR_EL3.CLUSTERPMUEN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERPMCEID0_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    if ACTLR_EL3.CLUSTERPMUEN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERPMCEID0_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERPMCEID0_EL1 = X[t];
```
