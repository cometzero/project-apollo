# IMP_CLUSTERPMSELR_EL1, Performance Monitors Event Counter Selection Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMSELR-EL1--Performance-Monitors-Event-Counter-Selection-Register>

### IMP\_CLUSTERPMSELR\_EL1, Performance Monitors Event Counter Selection Register

Selects the current event counter AArch64-IMP\_CLUSTERPMEVCNTR\_EL1.

IMP\_CLUSTERPMSELR\_EL1 is used in conjunction with AArch64-IMP\_CLUSTERPMXEVTYPER\_EL1 to determine the event that increments a selected event counter, and the modes and states in which the selected counter increments.

It is also used in conjunction with AArch64-IMP\_CLUSTERPMXEVCNTR\_EL1, to determine the value of a selected event counter.

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
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. AArch64\_imp\_clusterpmselr\_el1 bit assignments

![AArch64_imp_clusterpmselr_el1 bit assignments](images/0243-IMP_CLUSTERPMSELR_EL1-Performance-Monitors-Event-Counter-Selection-Register-img01.svg)

<table id="bed1733414882309__aimp_clusterpmselr_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERPMSELR_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e152" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e155" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e158" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d365911e161" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="bed1733414882309__63-5-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [4:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SEL
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Selects event counter, AArch64-IMP_CLUSTERPMXEVCNTR_EL1, where n is the value held in this field. This value identifies which event counter is accessed when a subsequent access to AArch64-IMP_CLUSTERPMXEVTYPER_EL1 or AArch64-IMP_CLUSTERPMXEVCNTR_EL1 occurs.
    </p>
    <p>
     This field can take any value from 0 (
     <span class="documents-g.number.bin">
      0b00000
     </span>
     ) to (PMCR.N)-1.
    </p>
    <ul>
     <li>
      A read or write of AArch64-IMP_CLUSTERPMXEVTYPER_EL1 is treated as
      <span class="documents-archterm">
       RAZ/WI
      </span>
      .
     </li>
     <li>
      A read or write of AArch64-IMP_CLUSTERPMXEVCNTR_EL1 is treated as
      <span class="documents-archterm">
       RAZ/WI
      </span>
      .
     </li>
    </ul>
    <p>
     If this field is set to a value greater than or equal to the number of counters accessible at the current Exception level, but not equal to 31:
    </p>
    <ul>
     <li>
      Direct reads of this field are treated as
      <span class="documents-archterm">
       RAZ/WI
      </span>
      .
     </li>
     <li>
      The results of access to AArch64-IMP_CLUSTERPMXEVTYPER_EL1 or AArch64-IMP_CLUSTERPMXEVCNTR_EL1 are treated as
      <span class="documents-archterm">
       RAZ/WI
      </span>
      .
     </li>
    </ul>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="bed1733414882309__id-4-0-reset" rowspan="1">
    <code>
     5{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C5\_5

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
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e279" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e282" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e285" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e288" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d365911e291" rowspan="1">
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
     0b0101
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b101
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_0\_C15\_C5\_5, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e356" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e359" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e362" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d365911e365" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d365911e368" rowspan="1">
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
     0b0101
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b101
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_0\_C15\_C5\_5

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERPMSELR_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERPMSELR_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERPMSELR_EL1;
```

MSR S3\_0\_C15\_C5\_5, <Xt>

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
        IMP_CLUSTERPMSELR_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    if ACTLR_EL3.CLUSTERPMUEN == '0' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        IMP_CLUSTERPMSELR_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERPMSELR_EL1 = X[t];
```
