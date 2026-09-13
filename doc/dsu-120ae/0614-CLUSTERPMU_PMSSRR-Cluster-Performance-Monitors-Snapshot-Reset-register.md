# CLUSTERPMU_PMSSRR, Cluster Performance Monitors Snapshot Reset register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMSSRR--Cluster-Performance-Monitors-Snapshot-Reset-register>

### CLUSTERPMU\_PMSSRR, Cluster Performance Monitors Snapshot Reset register

Configure PMU Snapshot to reset counters after each sample taken.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xE38

Access type
:   See bit descriptions

Reset value
:   ```
    x000 0000 0000 0000 0000 0000 00xx xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterpmu\_pmssrr bit assignments

![ext_clusterpmu_pmssrr bit assignments](images/0614-CLUSTERPMU_PMSSRR-Cluster-Performance-Monitors-Snapshot-Reset-register-img01.svg)

<table id="dqc1733415329612__aclusterpmu_pmssrr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMSSRR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d62090e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d62090e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d62090e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d62090e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="dqc1733415329612__31-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="dqc1733415329612__30-6-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RP5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reset performance counter. For each bit [x], if x &gt;= ext-CLUSTERPMU_PMCR.N, the number of implemented counters, then RP[x] is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     . Otherwise, indicates whether ext-PMEVCNTR&lt;x&gt; and ext-PMOVSR[x] are to be reset after a capture.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Do not reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="dqc1733415329612__id-5-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RP4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reset performance counter. For each bit [x], if x &gt;= ext-CLUSTERPMU_PMCR.N, the number of implemented counters, then RP[x] is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     . Otherwise, indicates whether ext-PMEVCNTR&lt;x&gt; and ext-PMOVSR[x] are to be reset after a capture.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Do not reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="dqc1733415329612__id-4-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RP3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reset performance counter. For each bit [x], if x &gt;= ext-CLUSTERPMU_PMCR.N, the number of implemented counters, then RP[x] is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     . Otherwise, indicates whether ext-PMEVCNTR&lt;x&gt; and ext-PMOVSR[x] are to be reset after a capture.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Do not reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="dqc1733415329612__id-3-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RP2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reset performance counter. For each bit [x], if x &gt;= ext-CLUSTERPMU_PMCR.N, the number of implemented counters, then RP[x] is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     . Otherwise, indicates whether ext-PMEVCNTR&lt;x&gt; and ext-PMOVSR[x] are to be reset after a capture.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Do not reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="dqc1733415329612__id-2-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RP1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reset performance counter. For each bit [x], if x &gt;= ext-CLUSTERPMU_PMCR.N, the number of implemented counters, then RP[x] is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     . Otherwise, indicates whether ext-PMEVCNTR&lt;x&gt; and ext-PMOVSR[x] are to be reset after a capture.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Do not reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="dqc1733415329612__id-1-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RP0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Reset performance counter. For each bit [x], if x &gt;= ext-CLUSTERPMU_PMCR.N, the number of implemented counters, then RP[x] is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     . Otherwise, indicates whether ext-PMEVCNTR&lt;x&gt; and ext-PMOVSR[x] are to be reset after a capture.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Do not reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Reset ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; and ext-CLUSTERPMU_PMOVSR[x] on capture.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="dqc1733415329612__id-0-reset" rowspan="1">
    <span>
     x
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
:   RW

Otherwise
:   ERROR
