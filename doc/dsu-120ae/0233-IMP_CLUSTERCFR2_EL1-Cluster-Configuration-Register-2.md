# IMP_CLUSTERCFR2_EL1, Cluster Configuration Register 2

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCFR2-EL1--Cluster-Configuration-Register-2>

### IMP\_CLUSTERCFR2\_EL1, Cluster Configuration Register 2

Contains details of the hardware configuration of the cluster.

### Configurations

AArch64 register IMP\_CLUSTERCFR2\_EL1 bits [63:0] are architecturally mapped to External System register [CLUSTERCFR2, Cluster Configuration Register 2](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERCFR2--Cluster-Configuration-Register-2?lang=en "Contains details of the hardware configuration of the cluster.") bits [63:0].

### Attributes

Width
:   64

Functional group
:   Generic System Control

Access type
:   See bit descriptions

Reset value
:   ```
    0000 0000 0000 0000 0000 00xx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. AArch64\_imp\_clustercfr2\_el1 bit assignments

![AArch64_imp_clustercfr2_el1 bit assignments](images/0233-IMP_CLUSTERCFR2_EL1-Cluster-Configuration-Register-2-img01.svg)

<table id="kgj1733414868598__aimp_clustercfr2_el1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERCFR2_EL1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e152" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e155" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e158" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d323352e161" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:42]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="kgj1733414868598__63-42-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [41:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CRS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Core register slices. Each three bits represents a core, with [2:0] for core 0 up to [41:39] for core 13.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000000
      </span>
     </dt>
     <dd>
      <p>
       No register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000001
      </span>
     </dt>
     <dd>
      <p>
       One register slice
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000010
      </span>
     </dt>
     <dd>
      <p>
       Two register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000011
      </span>
     </dt>
     <dd>
      <p>
       Three register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000100
      </span>
     </dt>
     <dd>
      <p>
       Four register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000101
      </span>
     </dt>
     <dd>
      <p>
       Five register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000110
      </span>
     </dt>
     <dd>
      <p>
       Six register slices
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000000000000000000000000000000000000000111
      </span>
     </dt>
     <dd>
      <p>
       Seven register slices
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="kgj1733414868598__id-41-0-reset" rowspan="1">
    <code>
     42{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_0\_C15\_C9\_2

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
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e366" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e369" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e372" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e375" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d323352e378" rowspan="1">
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
     0b010
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_0\_C15\_C9\_2, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e443" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e446" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e449" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d323352e452" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d323352e455" rowspan="1">
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
     0b010
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_0\_C15\_C9\_2

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        return IMP_CLUSTERCFR2_EL1;
elsif PSTATE.EL == EL2 then
    return IMP_CLUSTERCFR2_EL1;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERCFR2_EL1;
```

MSR S3\_0\_C15\_C9\_2, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        IMP_CLUSTERCFR2_EL1 = X[t];
elsif PSTATE.EL == EL2 then
    IMP_CLUSTERCFR2_EL1 = X[t];
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERCFR2_EL1 = X[t];
```
