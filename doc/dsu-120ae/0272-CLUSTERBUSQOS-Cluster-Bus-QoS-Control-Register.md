# CLUSTERBUSQOS, Cluster Bus QoS Control Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERBUSQOS--Cluster-Bus-QoS-Control-Register>

### CLUSTERBUSQOS, Cluster Bus QoS Control Register

Determines the value driven on the CHI bus QoS field.

### Configurations

External register CLUSTERBUSQOS bits [63:0] are architecturally mapped to AArch64 System register [IMP\_CLUSTERBUSQOS\_EL1, Cluster Bus QoS Control Register](/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERBUSQOS-EL1--Cluster-Bus-QoS-Control-Register?lang=en "Determines the value driven on the CHI bus QoS field.") bits [63:0].

### Attributes

Width
:   64

Component
:   Cluster

Register offset
:   0x0048

Access type
:   RW

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 1110 1110 1011 1110

### Bit descriptions

Figure 1. ext\_clusterbusqos bit assignments

![ext_clusterbusqos bit assignments](images/0272-CLUSTERBUSQOS-Cluster-Bus-QoS-Control-Register-img01.svg)

<table id="oea1733414861450__aclusterbusqos-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERBUSQOS bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d306853e147" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d306853e150" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d306853e153" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d306853e156" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="oea1733414861450__63-16-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACP1QOS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Valid driven on the CHI bus QoS field for acp 1 accesses.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="oea1733414861450__id-15-12-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1110
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACP0QOS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Valid driven on the CHI bus QoS field for acp 0 accesses.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="oea1733414861450__id-11-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1110
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Valid driven on the CHI bus QoS field for prefetches.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="oea1733414861450__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1011
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    QOS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Valid driven on the CHI bus QoS field for demand accesses.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="oea1733414861450__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1110
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
   <th class="documents-nocellnorowborder" colspan="1" id="d306853e294" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d306853e297" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d306853e300" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d306853e303" rowspan="1">
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
    0x0048
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERBUSQOS
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
