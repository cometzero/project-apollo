# IMP_CLUSTERCDBG_EL3, Cluster Cache Debug Register

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCDBG-EL3--Cluster-Cache-Debug-Register>

### IMP\_CLUSTERCDBG\_EL3, Cluster Cache Debug Register

Can be used to read the contents of the L3 cache RAMs and snoop filter RAMs. The register must be written with the information of which RAM is to be read. Then the same register should be read to read the contents of that RAM.

### Configurations

This register is available in all configurations.

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

Figure 1. AArch64\_imp\_clustercdbg\_el3 bit assignments

![AArch64_imp_clustercdbg_el3 bit assignments](images/0235-IMP_CLUSTERCDBG_EL3-Cluster-Cache-Debug-Register-img01.svg)

<table id="gfv1733414872023__aimp_clustercdbg_el3-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   IMP_CLUSTERCDBG_EL3 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e138" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e141" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e144" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d251550e147" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="gfv1733414872023__63-32-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
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
     Way of RAM being accessed.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gfv1733414872023__id-31-28-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gfv1733414872023__27-24-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SLCID_IDX
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The L3 cache Set locations in each cache slice are all power-of-2 in size and therefore can be identified using contiguous index locations.
    </p>
    <p>
     The Set index values for slice 0 start from value zero in this field, followed by the index locations for slice 1, then slice 2, and so on.
    </p>
    <p>
     The total index width varies depending on the size of the RAM being accessed. The cache slice identification number, Slice ID, forms the upper
    </p>
    <p>
     used bits of the cache location encoding in this field.
    </p>
    <p>
     For a Tag RAM or Data RAM access this field will encode as {'0, SLICE_ID_W, TagRAM_IDX_W}
    </p>
    <p>
     For a Snoop Filter RAM access this field will encode as {'0, SLICE_ID_W, SFRAM_IDX_W}.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gfv1733414872023__id-23-6-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000000000000000000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5:3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CHUNK
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Select of 64-bit data chunk to read from 512-bit Data RAM cache line. Only used when accessing Data RAM data.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       Data[63:0]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       Data[127:64]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       Data[191:128]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       Data[255:192]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b100
      </span>
     </dt>
     <dd>
      <p>
       Data[319:256]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101
      </span>
     </dt>
     <dd>
      <p>
       Data[383:320]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b110
      </span>
     </dt>
     <dd>
      <p>
       Data[447:384]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       Data[511:448]
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gfv1733414872023__id-5-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [2:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RAM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RAM to be accessed. All other values are reserved.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       Snoop Filter RAM
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       Tag RAM
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       Data RAM - accessing cacheline data
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       Data RAM - accessing cacheline MTE tags
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="gfv1733414872023__id-2-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Access

MRS <Xt>, S3\_6\_C15\_C4\_7

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
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e513" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e516" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e519" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e522" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d251550e525" rowspan="1">
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
     0b110
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
     0b111
    </span>
   </td>
  </tr>
 </tbody>
</table>

MSR S3\_6\_C15\_C4\_7, <Xt>

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
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e590" rowspan="1">
    op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e593" rowspan="1">
    op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e596" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d251550e599" rowspan="1">
    CRm
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d251550e602" rowspan="1">
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
     0b110
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
     0b111
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

MRS <Xt>, S3\_6\_C15\_C4\_7

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        UNDEFINED;
elsif PSTATE.EL == EL2 then
    UNDEFINED;
elsif PSTATE.EL == EL3 then
    return IMP_CLUSTERCDBG_EL3;
```

MSR S3\_6\_C15\_C4\_7, <Xt>

```
if PSTATE.EL == EL0 then
    UNDEFINED;
elsif PSTATE.EL == EL1 then
    if EL2Enabled() && HCR_EL2.TIDCP == '1' then
        AArch64.SystemAccessTrap(EL2, 0x18);
    else
        UNDEFINED;
elsif PSTATE.EL == EL2 then
    UNDEFINED;
elsif PSTATE.EL == EL3 then
    IMP_CLUSTERCDBG_EL3 = X[t];
```
