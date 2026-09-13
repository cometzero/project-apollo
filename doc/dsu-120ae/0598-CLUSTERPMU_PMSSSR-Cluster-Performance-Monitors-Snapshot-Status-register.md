# CLUSTERPMU_PMSSSR, Cluster Performance Monitors Snapshot Status register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMSSSR--Cluster-Performance-Monitors-Snapshot-Status-register>

### CLUSTERPMU\_PMSSSR, Cluster Performance Monitors Snapshot Status register

Holds status information about the captured counters.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0x638

Access type
:   See bit descriptions

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxx1
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterpmu\_pmsssr bit assignments

![ext_clusterpmu_pmsssr bit assignments](images/0598-CLUSTERPMU_PMSSSR-Cluster-Performance-Monitors-Snapshot-Status-register-img01.svg)

<table id="tgf1733415304941__aclusterpmu_pmsssr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMSSSR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d266817e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d266817e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d266817e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d266817e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="tgf1733415304941__31-1-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    NC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     No capture. Indicates whether the PMU counters have been captured.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       PMU counters captured.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       PMU counters not captured.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="tgf1733415304941__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
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
