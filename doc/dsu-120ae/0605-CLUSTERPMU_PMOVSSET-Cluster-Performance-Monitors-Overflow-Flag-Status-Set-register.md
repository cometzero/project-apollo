# CLUSTERPMU_PMOVSSET, Cluster Performance Monitors Overflow Flag Status Set register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMOVSSET--Cluster-Performance-Monitors-Overflow-Flag-Status-Set-register>

### CLUSTERPMU\_PMOVSSET, Cluster Performance Monitors Overflow Flag Status Set register

Sets the state of the overflow bit for each of the implemented event counters AArch64-PMEVCNTR<n>.

### Configurations

External register CLUSTERPMU\_PMOVSSET bits [31:0] are architecturally mapped to AArch64 System register [IMP\_CLUSTERPMOVSSET\_EL1, Performance Monitors Overflow Flag Status Set Register](/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMOVSSET-EL1--Performance-Monitors-Overflow-Flag-Status-Set-Register?lang=en "Sets the state of the overflow bit for each of the implemented event counters AArch64-PMXEVCNTR_EL1.") bits [31:0].

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xCC0

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

Figure 1. ext\_clusterpmu\_pmovsset bit assignments

![ext_clusterpmu_pmovsset bit assignments](images/0605-CLUSTERPMU_PMOVSSET-Cluster-Performance-Monitors-Overflow-Flag-Status-Set-register-img01.svg)

<table id="aqd1733415314212__aclusterpmu_pmovsset-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMOVSSET bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d353073e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d353073e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d353073e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d353073e160" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="aqd1733415314212__31-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="aqd1733415314212__30-6-reset" rowspan="1">
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
    P5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter overflow set bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;. Bits [30:ext-CLUSTERPMU_PMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has not overflowed since this bit was last cleared. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has overflowed since this bit was last cleared. When written, sets the ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; overflow bit to 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="aqd1733415314212__id-5-reset" rowspan="1">
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
    P4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter overflow set bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;. Bits [30:ext-CLUSTERPMU_PMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has not overflowed since this bit was last cleared. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has overflowed since this bit was last cleared. When written, sets the ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; overflow bit to 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="aqd1733415314212__id-4-reset" rowspan="1">
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
    P3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter overflow set bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;. Bits [30:ext-CLUSTERPMU_PMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has not overflowed since this bit was last cleared. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has overflowed since this bit was last cleared. When written, sets the ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; overflow bit to 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="aqd1733415314212__id-3-reset" rowspan="1">
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
    P2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter overflow set bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;. Bits [30:ext-CLUSTERPMU_PMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has not overflowed since this bit was last cleared. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has overflowed since this bit was last cleared. When written, sets the ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; overflow bit to 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="aqd1733415314212__id-2-reset" rowspan="1">
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
    P1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter overflow set bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;. Bits [30:ext-CLUSTERPMU_PMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has not overflowed since this bit was last cleared. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has overflowed since this bit was last cleared. When written, sets the ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; overflow bit to 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="aqd1733415314212__id-1-reset" rowspan="1">
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
    P0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Event counter overflow set bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;. Bits [30:ext-CLUSTERPMU_PMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has not overflowed since this bit was last cleared. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; has overflowed since this bit was last cleared. When written, sets the ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; overflow bit to 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="aqd1733415314212__id-0-reset" rowspan="1">
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
