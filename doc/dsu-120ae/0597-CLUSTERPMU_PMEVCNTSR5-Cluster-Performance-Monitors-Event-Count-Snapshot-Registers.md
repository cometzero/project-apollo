# CLUSTERPMU_PMEVCNTSR5, Cluster Performance Monitors Event Count Snapshot Registers

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR5--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers>

### CLUSTERPMU\_PMEVCNTSR5, Cluster Performance Monitors Event Count Snapshot Registers

Holds event counter 5, which counts events.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   CLUSTERPMU

Register offset
:   0x628

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

Figure 1. ext\_clusterpmu\_pmevcntsr5 bit assignments

![ext_clusterpmu_pmevcntsr5 bit assignments](images/0597-CLUSTERPMU_PMEVCNTSR5-Cluster-Performance-Monitors-Event-Count-Snapshot-Registers-img01.svg)

<table id="iyz1733415304069__aclusterpmu_pmevcntsr5-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMEVCNTSR5 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d230616e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d230616e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d230616e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d230616e150" rowspan="1">
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
    PMEVCNTSR
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Event counter 5.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="iyz1733415304069__id-63-0-reset" rowspan="1">
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
:   RO

Otherwise
:   ERROR
