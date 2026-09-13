# IMP_CLUSTERPWRSTAT_EL1, Cluster Power Status Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRSTAT-EL1--Cluster-Power-Status-Register>

### IMP\_CLUSTERPWRSTAT\_EL1, Cluster Power Status Register

This register contains the current status of power features and is read-only.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Functional group
:   Generic System Control

Access type
:   RO

Reset value
:   ```
    0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 xxxx 0000
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. AArch64\_imp\_clusterpwrstat\_el1 bit assignments

![AArch64_imp_clusterpwrstat_el1 bit assignments](images/0223-IMP_CLUSTERPWRSTAT_EL1-Cluster-Power-Status-Register-img01.svg)

<table id="pkc1733414851322__aimp_clusterpwrstat_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERPWRSTAT_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e142" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e145" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e148" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d103743e151" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pkc1733414851322__63-8-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SLC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Cache slice power status. This indicates which cache slices are currently powered up and available. It can be used to determine when the state requested in bits [7:6] of the IMP_CLUSTERPWRCTLR_EL1 has taken effect.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pkc1733414851322__id-7-6-reset" rowspan="1">
    <span>
     xx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    POR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Cache portion power status. This indicates which cache portions are currently powered up and available. It can be used to determine when the state requested in bits [5:4] of the IMP_CLUSTERPWRCTLR_EL1 has taken effect.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pkc1733414851322__id-5-4-reset" rowspan="1">
    <span>
     xx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3:2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pkc1733414851322__3-2-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MEMRET
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable memory retention when all cores are powered down. Note this bit is a combined version of all banked per-thread bits from the IMP_CLUSTERPWRDN_EL1 register.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pkc1733414851322__id-1-reset" rowspan="1">
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
    PWRDN
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Disable cluster power down when all cores are powered down. Note this bit is a combined version of all banked per-thread bits from the IMP_CLUSTERPWRDN_EL1 register.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="pkc1733414851322__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C3\_7

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
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e317" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e320" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e323" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e326" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d103743e329" rowspan="1">
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
     0b111
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_0\_C15\_C3\_7, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e394" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e397" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e400" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103743e403" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d103743e406" rowspan="1">
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
     0b111
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_0\_C15\_C3\_7

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERPWRSTAT_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERPWRSTAT_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERPWRSTAT_EL1;
```

MSR S3\_0\_C15\_C3\_7, <Xt>

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
        IMP_CLUSTERPWRSTAT_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    if Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && ACTLR_EL3.PWREN == '0' then
        UNDEFINED;
    elsif ACTLR_EL3.PWREN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERPWRSTAT_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERPWRSTAT_EL1 = X[t];
```
