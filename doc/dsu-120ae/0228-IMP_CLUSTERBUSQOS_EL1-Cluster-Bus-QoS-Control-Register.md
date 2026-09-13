# IMP_CLUSTERBUSQOS_EL1, Cluster Bus QoS Control Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERBUSQOS-EL1--Cluster-Bus-QoS-Control-Register>

### IMP\_CLUSTERBUSQOS\_EL1, Cluster Bus QoS Control Register

Determines the value driven on the CHI bus QoS field.

### Configurations

AArch64 register IMP\_CLUSTERBUSQOS\_EL1 bits [63:0] are architecturally mapped to External System register [CLUSTERBUSQOS, Cluster Bus QoS Control Register](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERBUSQOS--Cluster-Bus-QoS-Control-Register?lang=en "Determines the value driven on the CHI bus QoS field.") bits [63:0].

### Attributes

Width
:   64

Functional group
:   Generic System Control

Access type
:   See bit descriptions

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 1110 1110 1011 1110

### Bit descriptions

Figure 1. AArch64\_imp\_clusterbusqos\_el1 bit assignments

![AArch64_imp_clusterbusqos_el1 bit assignments](images/0228-IMP_CLUSTERBUSQOS_EL1-Cluster-Bus-QoS-Control-Register-img01.svg)

<table id="oke1733414862467__aimp_clusterbusqos_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERBUSQOS_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e148" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e151" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e154" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d95132e157" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oke1733414862467__63-16-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oke1733414862467__id-15-12-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oke1733414862467__id-11-8-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oke1733414862467__id-7-4-reset" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="oke1733414862467__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1110
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C4\_4

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
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e301" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e304" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e307" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e310" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d95132e313" rowspan="1">
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
     0b0100
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

MSR S3\_0\_C15\_C4\_4, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e378" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e381" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e384" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95132e387" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d95132e390" rowspan="1">
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
     0b0100
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

MRS <Xt>, S3\_0\_C15\_C4\_4

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERBUSQOS_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERBUSQOS_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERBUSQOS_EL1;
```

MSR S3\_0\_C15\_C4\_4, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && ACTLR_EL3.QOSEN == '0' then
        UNDEFINED;
    elsif EL2Enabled() && ACTLR_EL2.QOSEN == '0' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif ACTLR_EL3.QOSEN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERBUSQOS_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    if Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && ACTLR_EL3.QOSEN == '0' then
        UNDEFINED;
    elsif ACTLR_EL3.QOSEN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERBUSQOS_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERBUSQOS_EL1 = X[t];
```
