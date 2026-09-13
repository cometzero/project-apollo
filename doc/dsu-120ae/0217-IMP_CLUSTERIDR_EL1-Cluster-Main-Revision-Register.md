# IMP_CLUSTERIDR_EL1, Cluster Main Revision Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERIDR-EL1--Cluster-Main-Revision-Register>

### IMP\_CLUSTERIDR\_EL1, Cluster Main Revision Register

Holds the revision and patch level of the cluster.

### Configurations

AArch64 register IMP\_CLUSTERIDR\_EL1 bits [63:0] are architecturally mapped to External System register [CLUSTERIDR, Cluster Main Revision Register](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERIDR--Cluster-Main-Revision-Register?lang=en "Holds the revision and patch level of the cluster.") bits [63:0].

### Attributes

Width
:   64

Functional group
:   Generic System Control

Access type
:   See bit descriptions

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx 0000 0001
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. AArch64\_imp\_clusteridr\_el1 bit assignments

![AArch64_imp_clusteridr_el1 bit assignments](images/0217-IMP_CLUSTERIDR_EL1-Cluster-Main-Revision-Register-img01.svg)

<table id="spc1733414833599__aimp_clusteridr_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERIDR_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e152" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e155" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e158" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d229780e161" rowspan="1">
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
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="spc1733414833599__63-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Variant
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates the variant of the DSU. This is the major revision number x in the rx part of the rxpy description of the product revision status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Cluster major revision 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="spc1733414833599__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Revision
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Indicates the minor revision number of the DSU. This is the minor revision number y in the py part of the rxpy description of the product revision status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Cluster minor revision 0.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Cluster minor revision 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="spc1733414833599__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C3\_1

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
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e314" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e317" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e320" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e323" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d229780e326" rowspan="1">
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
     0b001
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_0\_C15\_C3\_1, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e391" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e394" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e397" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d229780e400" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d229780e403" rowspan="1">
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
     0b001
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_0\_C15\_C3\_1

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERIDR_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERIDR_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERIDR_EL1;
```

MSR S3\_0\_C15\_C3\_1, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        IMP_CLUSTERIDR_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    IMP_CLUSTERIDR_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERIDR_EL1 = X[t];
```
