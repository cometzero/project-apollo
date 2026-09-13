# ERXMISC0_EL1, Selected Error Record Miscellaneous Register 0

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC0-EL1--Selected-Error-Record-Miscellaneous-Register-0>

### ERXMISC0\_EL1, Selected Error Record Miscellaneous Register 0

Accesses ext-CLUSTERRAS\_ERR0MISC0 when the value in AArch64-ERRSELR\_EL1.SEL is set to 0.

Miscellaneous error syndrome register. The Miscellaneous error syndrome register contains:

- 2 architecturally-defined Corrected error counters with sticky overflow bits,
- Information to identify the FRU in which the error was detected, including Index, Way, Level, Instruction vs. Data fields.

### Configurations

AArch64 register ERXMISC0\_EL1 bits [63:0] are architecturally mapped to External System register [CLUSTERRAS\_ERR0MISC0, Error Record Miscellaneous Register 0](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC0--Error-Record-Miscellaneous-Register-0?lang=en "Miscellaneous error syndrome register. The Miscellaneous error syndrome register contains:") bits [63:0].

### Attributes

Width
:   64

Functional group
:   RAS registers

Access type
:   See bit descriptions

Reset value
:   ```
    0000 0000 0000 0000 xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. AArch64\_erxmisc0\_el1 bit assignments

![AArch64_erxmisc0_el1 bit assignments](images/0258-ERXMISC0_EL1-Selected-Error-Record-Miscellaneous-Register-0-img01.svg)

<table id="ejk1733414915550__aerxmisc0_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   ERXMISC0_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e174" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e177" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e180" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d232621e183" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:48]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__63-48-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [47]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OFO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Sticky overflow bit for Other errors.
    </p>
    <p>
     Set to 1 when the Corrected error count Other (CECO) field is incremented and wraps through zero.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Other counter has not overflowed.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Other counter has overflowed.
      </p>
     </dd>
    </dl>
    <p>
     A direct write that modifies this bit might indirectly set ext-CLUSTERRAS_ERR0STATUS.OF to an
     <span class="documents-archterm">
      UNKNOWN
     </span>
     value and a direct write to ext-CLUSTERRAS_ERR0STATUS.OF that clears it to zero might indirectly set this bit to an
     <span class="documents-archterm">
      UNKNOWN
     </span>
     value.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__id-47-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [46:40]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CECO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Corrected error count for Other errors.
    </p>
    <p>
     The Other error counter increments for all Corrected errors that are not counted by the CECR Repeat error counter due to the syndrome of the new error mismatching against the recorded syndrome of the first Repeat error. Refer to the CECR Repeat error description for fields used to match syndrome.
    </p>
    <p>
     At most 1 error can be counted per clock cycle even if there are multiple Corrected errors and/or sources.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__id-46-40-reset" rowspan="1">
    <code>
     7{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [39]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OFR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Sticky overflow bit for Repeat errors.
    </p>
    <p>
     Set to 1 when the Corrected error count Repeat (CECR) field is incremented and wraps through zero.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Repeat counter has not overflowed.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Repeat counter has overflowed.
      </p>
     </dd>
    </dl>
    <p>
     A direct write that modifies this bit might indirectly set ext-CLUSTERRAS_ERR0STATUS.OF to an
     <span class="documents-archterm">
      UNKNOWN
     </span>
     value and a direct write to ext-CLUSTERRAS_ERR0STATUS.OF that clears it to zero might indirectly set this bit to an
     <span class="documents-archterm">
      UNKNOWN
     </span>
     value.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__id-39-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [38:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CECR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Corrected error count for Repeat errors.
    </p>
    <p>
     The Repeat error counter increments for the first Corrected error and records the syndrome for the error in the fields described below. It also increments for each subsequent Corrected error with a syndrome matching the first error's recorded syndrome, otherwise the error causes an increment to the CECO Other counter.
    </p>
    <p>
     The syndrome is recorded in the following fields:
    </p>
    <ul>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.IERR
      </p>
     </li>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.SERR
      </p>
     </li>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0MISC0.INDX
      </p>
     </li>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0MISC0.WAY
      </p>
     </li>
    </ul>
    <p>
     The syndrome is matched on a new Corrected error if all of the following are true:
    </p>
    <ul>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.MV bit is set,
      </p>
     </li>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.IERR matches the new error,
      </p>
     </li>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.SERR matches the new error,
      </p>
     </li>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0MISC0.INDX matches the new error,
      </p>
     </li>
     <li>
      <p>
       ext-CLUSTERRAS_ERR0MISC0.WAY matches the new error.
      </p>
     </li>
    </ul>
    <p>
     CLUSTERRAS_ERR0STATUS.MV indicates the validity of the INDX and WAY fields of the CLUSTERRAS_ERR0MISC0 register
    </p>
    <p>
     At most 1 error can be counted per clock cycle even if there are multiple Corrected errors and/or sources.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__id-38-32-reset" rowspan="1">
    <code>
     7{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WAY
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     L3 Cache Way that contained the error.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__id-31-28-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__27-24-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INDX
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     L3 Cache Index that contained the error.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__id-23-6-reset" rowspan="1">
    <code>
     18{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__5-4-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3:1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    LVL
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     L3 Cache-level that contained the error. Always
     <span class="documents-g.number.hex">
      0x2
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       L3 cache.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ejk1733414915550__id-3-1-reset" rowspan="1">
    <span>
     xxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    IND
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     L3 Cache instruction vs. data cache that contained the error. Always data (
     <span class="documents-g.number.hex">
      0x0
     </span>
     ).
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Data cache error.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="ejk1733414915550__id-0-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, ERXMISC0\_EL1

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
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e620" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e623" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e626" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e629" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d232621e632" rowspan="1">
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
     0b0101
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0101
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR ERXMISC0\_EL1, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e697" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e700" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e703" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d232621e706" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d232621e709" rowspan="1">
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
     0b0101
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0101
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, ERXMISC0\_EL1

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && SCR_EL3.TERR == '1' then
        UNDEFINED;
    elsif EL2Enabled() && HCR_EL2.TERR == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif EL2Enabled() && SCR_EL3.FGTEn == '1' && HFGRTR_EL2.ERXMISCn_EL1 == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif SCR_EL3.TERR == '1' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        return ERXMISC0_EL1;
elsif PSTATE.EL == EL2 then
    if Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && SCR_EL3.TERR == '1' then
        UNDEFINED;
    elsif SCR_EL3.TERR == '1' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        return ERXMISC0_EL1;
elsif PSTATE.EL == EL3 then
    return ERXMISC0_EL1;
```

MSR ERXMISC0\_EL1, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && SCR_EL3.TERR == '1' then
        UNDEFINED;
    elsif EL2Enabled() && HCR_EL2.TERR == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif EL2Enabled() && SCR_EL3.FGTEn == '1' && HFGWTR_EL2.ERXMISCn_EL1 == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    elsif SCR_EL3.TERR == '1' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        ERXMISC0_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    if Halted() && EDSCR.SDD == '1' && boolean IMPLEMENTATION_DEFINED "EL3 trap priority when SDD == '1'" && SCR_EL3.TERR == '1' then
        UNDEFINED;
    elsif SCR_EL3.TERR == '1' then
        if Halted() && EDSCR.SDD == '1' then
            UNDEFINED;
        else
            AArch64.SystemAccessTrap(EL3, 0x18);
    else
        ERXMISC0_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    ERXMISC0_EL1 = X[t];
```
