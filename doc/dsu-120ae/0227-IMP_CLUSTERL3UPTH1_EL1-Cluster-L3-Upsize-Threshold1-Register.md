# IMP_CLUSTERL3UPTH1_EL1, Cluster L3 Upsize Threshold1 Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3UPTH1-EL1--Cluster-L3-Upsize-Threshold1-Register>

### IMP\_CLUSTERL3UPTH1\_EL1, Cluster L3 Upsize Threshold1 Register

This register is intended for use in algorithms for determining when to power up or down cache portions.

### Configurations

AArch64 register IMP\_CLUSTERL3UPTH1\_EL1 bits [63:0] are architecturally mapped to External System register [CLUSTERL3UPTH1, Cluster L3 Upsize Threshold1 Register](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERL3UPTH1--Cluster-L3-Upsize-Threshold1-Register?lang=en "This register is intended for use in algorithms for determining when to power up or down cache portions.") bits [63:0].

### Attributes

Width
:   64

Functional group
:   Generic System Control

Access type
:   See bit descriptions

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. AArch64\_imp\_clusterl3upth1\_el1 bit assignments

![AArch64_imp_clusterl3upth1_el1 bit assignments](images/0227-IMP_CLUSTERL3UPTH1_EL1-Cluster-L3-Upsize-Threshold1-Register-img01.svg)

<table id="mfp1733414860155__aimp_clusterl3upth1_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERL3UPTH1_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e148" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e151" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e154" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d335104e157" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="mfp1733414860155__63-32-reset" rowspan="1">
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
    UPTH1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     If half of the L3 cache ways are powered, and the L3 cache miss bandwidth rises above this threshold then the L3 cache is upsized to all of the ways. The value in this register is compared with the change in the cluster L3 miss counter since the last time period.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="mfp1733414860155__id-31-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C4\_3

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
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e238" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e241" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e244" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e247" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d335104e250" rowspan="1">
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
     0b011
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_0\_C15\_C4\_3, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e315" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e318" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e321" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d335104e324" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d335104e327" rowspan="1">
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
     0b011
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_0\_C15\_C4\_3

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERL3UPTH1_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERL3UPTH1_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERL3UPTH1_EL1;
```

MSR S3\_0\_C15\_C4\_3, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && ACTLR_EL3.PWREN == '0' then
        UNDEFINED;
    elsif EL2Enabled() && ACTLR_EL2.PWREN == '0' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif ACTLR_EL3.PWREN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERL3UPTH1_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    if Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && ACTLR_EL3.PWREN == '0' then
        UNDEFINED;
    elsif ACTLR_EL3.PWREN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERL3UPTH1_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERL3UPTH1_EL1 = X[t];
```
