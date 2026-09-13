# CLUSTERREVIDR, Cluster ECO ID Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERREVIDR--Cluster-ECO-ID-Register>

### CLUSTERREVIDR, Cluster ECO ID Register

Enables ECO patches to be applied to the cluster-level to be identified by software.

### Configurations

External register CLUSTERREVIDR bits [63:0] are architecturally mapped to AArch64 System register [IMP\_CLUSTERREVIDR\_EL1, Cluster ECO ID Register](/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERREVIDR-EL1--Cluster-ECO-ID-Register?lang=en "Enables ECO patches to be applied to the cluster-level to be identified by software.") bits [63:0].

### Attributes

Width
:   64

Component
:   Cluster

Register offset
:   0x0008

Access type
:   RO

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_clusterrevidr bit assignments

![ext_clusterrevidr bit assignments](images/0266-CLUSTERREVIDR-Cluster-ECO-ID-Register-img01.svg)

<table id="kac1733414836951__aclusterrevidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERREVIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d134038e147" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134038e150" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134038e153" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d134038e156" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="kac1733414836951__id-63-0-reset-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x0000000000000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table id="kac1733414836951__table_w2024ab1b9b7b3_w2025ab1b9b7_w2026ab1b9_w2027ab1">
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d134038e228" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134038e231" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d134038e234" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d134038e237" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Cluster
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0008
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERREVIDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
