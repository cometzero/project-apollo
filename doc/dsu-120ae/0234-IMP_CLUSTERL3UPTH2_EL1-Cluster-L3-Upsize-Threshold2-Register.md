# IMP_CLUSTERL3UPTH2_EL1, Cluster L3 Upsize Threshold2 Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3UPTH2-EL1--Cluster-L3-Upsize-Threshold2-Register>

### IMP\_CLUSTERL3UPTH2\_EL1, Cluster L3 Upsize Threshold2 Register

This register is intended for use in algorithms for determining when to power up slices.

### Configurations

AArch64 register IMP\_CLUSTERL3UPTH2\_EL1 bits [63:0] are architecturally mapped to External System register [CLUSTERL3UPTH2, Cluster L3 Upsize Threshold2 Register](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERL3UPTH2--Cluster-L3-Upsize-Threshold2-Register?lang=en "This register is intended for use in algorithms for determining when to power up slices.") bits [63:0].

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

Figure 1. AArch64\_imp\_clusterl3upth2\_el1 bit assignments

![AArch64_imp_clusterl3upth2_el1 bit assignments](images/0234-IMP_CLUSTERL3UPTH2_EL1-Cluster-L3-Upsize-Threshold2-Register-img01.svg)

<table id="aky1733414870734__aimp_clusterl3upth2_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERL3UPTH2_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e148" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e151" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e154" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d362222e157" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="aky1733414870734__63-32-reset" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="aky1733414870734__id-31-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C9\_3

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
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e238" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e241" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e244" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e247" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d362222e250" rowspan="1">
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
     0b1001
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

MSR S3\_0\_C15\_C9\_3, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e315" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e318" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e321" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d362222e324" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d362222e327" rowspan="1">
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
     0b1001
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

MRS <Xt>, S3\_0\_C15\_C9\_3

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERL3UPTH2_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERL3UPTH2_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERL3UPTH2_EL1;
```

MSR S3\_0\_C15\_C9\_3, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        IMP_CLUSTERL3UPTH2_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    IMP_CLUSTERL3UPTH2_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERL3UPTH2_EL1 = X[t];
```
