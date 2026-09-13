# CLUSTERPMU_PMEVCNTR4, Cluster Performance Monitors Event Count Registers

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR4--Cluster-Performance-Monitors-Event-Count-Registers>

### CLUSTERPMU\_PMEVCNTR4, Cluster Performance Monitors Event Count Registers

Holds event counter 4, which counts events.

### Configurations

External register CLUSTERPMU\_PMEVCNTR4 bits [63:0] are architecturally mapped to AArch64 System register [IMP\_CLUSTERPMXEVCNTR\_EL1, Performance Monitors Selected Event Count Register](/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMXEVCNTR-EL1--Performance-Monitors-Selected-Event-Count-Register?lang=en "Reads or writes the value of the selected event counter, AArch64-IMP_CLUSTERPMXEVCNTR_EL1. AArch64-IMP_CLUSTERPMSELR_EL1.SEL determines which event counter is selected.") bits [63:0].

### Attributes

Width
:   64

Component
:   CLUSTERPMU

Register offset
:   0x20

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

Figure 1. ext\_clusterpmu\_pmevcntr4 bit assignments

![ext_clusterpmu_pmevcntr4 bit assignments](images/0584-CLUSTERPMU_PMEVCNTR4-Cluster-Performance-Monitors-Event-Count-Registers-img01.svg)

<table id="cuy1733415289366__aclusterpmu_pmevcntr4-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMEVCNTR4 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d235033e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d235033e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d235033e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d235033e160" rowspan="1">
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
    PMEVCNTR
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Event counter 4.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="cuy1733415289366__id-63-0-reset-1" rowspan="1">
    <code>
     64{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

When IsCorePowered() && !DoubleLockStatus() && !OSLockStatus() && AllowExternalPMUAccess() && SoftwareLockStatus()
:   RO

When IsCorePowered() && !DoubleLockStatus() && !OSLockStatus() && AllowExternalPMUAccess() && !SoftwareLockStatus()
:   RW

Otherwise
:   ERROR
