# IMP_CLUSTERREVIDR_EL1, Cluster ECO ID Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERREVIDR-EL1--Cluster-ECO-ID-Register>

### IMP\_CLUSTERREVIDR\_EL1, Cluster ECO ID Register

Enables ECO patches to be applied to the cluster-level to be identified by software.

### Configurations

AArch64 register IMP\_CLUSTERREVIDR\_EL1 bits [63:0] are architecturally mapped to External System register [CLUSTERREVIDR, Cluster ECO ID Register](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERREVIDR--Cluster-ECO-ID-Register?lang=en "Enables ECO patches to be applied to the cluster-level to be identified by software.") bits [63:0].

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

Figure 1. AArch64\_imp\_clusterrevidr\_el1 bit assignments

![AArch64_imp_clusterrevidr_el1 bit assignments](images/0218-IMP_CLUSTERREVIDR_EL1-Cluster-ECO-ID-Register-img01.svg)

<table id="rkv1733414839847__aimp_clusterrevidr_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERREVIDR_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e148" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e151" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e154" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d336354e157" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [63:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ECOID
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Contains ECO information. Refer to the errata documentation for any bit allocations.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000000000000000000000000000000000000000000000000000000000000000
      </span>
     </dt>
     <dd>
      <p>
       Customer ECO ID
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="rkv1733414839847__id-63-0-reset-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x0000000000000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C3\_2

<table id="rkv1733414839847__table_w2047ab1b9b7b5_w2048ab1b9b7_w2049ab1b9_w2050ab1">
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e235" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e238" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e241" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e244" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d336354e247" rowspan="1">
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
     0b0011
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b010
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_0\_C15\_C3\_2, <Xt>

<table id="rkv1733414839847__table_w2051ab1b9b7b9_w2052ab1b9b7_w2053ab1b9_w2054ab1">
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e312" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e315" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e318" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d336354e321" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d336354e324" rowspan="1">
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
     0b0011
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b010
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_0\_C15\_C3\_2

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERREVIDR_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERREVIDR_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERREVIDR_EL1;
```

MSR S3\_0\_C15\_C3\_2, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        IMP_CLUSTERREVIDR_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    IMP_CLUSTERREVIDR_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERREVIDR_EL1 = X[t];
```
