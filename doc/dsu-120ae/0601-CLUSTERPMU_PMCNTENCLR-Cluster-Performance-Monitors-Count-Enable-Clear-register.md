# CLUSTERPMU_PMCNTENCLR, Cluster Performance Monitors Count Enable Clear register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCNTENCLR--Cluster-Performance-Monitors-Count-Enable-Clear-register>

### CLUSTERPMU\_PMCNTENCLR, Cluster Performance Monitors Count Enable Clear register

Disables any implemented event counters AArch64-IMP\_CLUSTERPMEVCNTR<n>.

### Configurations

External register CLUSTERPMU\_PMCNTENCLR bits [31:0] are architecturally mapped to AArch64 System register [IMP\_CLUSTERPMCNTENCLR\_EL1, Performance Monitors Count Enable Clear Register](/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCNTENCLR-EL1--Performance-Monitors-Count-Enable-Clear-Register?lang=en "Disables all implemented event counters AArch64-IMP_CLUSTERPMXEVCNTR_EL1.") bits [31:0].

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xC20

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

Figure 1. ext\_clusterpmu\_pmcntenclr bit assignments

![ext_clusterpmu_pmcntenclr bit assignments](images/0601-CLUSTERPMU_PMCNTENCLR-Cluster-Performance-Monitors-Count-Enable-Clear-register-img01.svg)

<table id="wsl1733415308126__aclusterpmu_pmcntenclr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMCNTENCLR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d209701e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d209701e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d209701e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d209701e160" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="wsl1733415308126__31-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="wsl1733415308126__30-6-reset" rowspan="1">
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
     Event counter disable bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERPMU_PMCFGR.N is less than 31, bits [30:ext-CLUSTERPMU_PMCFGR.N] are
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
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wsl1733415308126__id-5-reset" rowspan="1">
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
     Event counter disable bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERPMU_PMCFGR.N is less than 31, bits [30:ext-CLUSTERPMU_PMCFGR.N] are
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
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wsl1733415308126__id-4-reset" rowspan="1">
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
     Event counter disable bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERPMU_PMCFGR.N is less than 31, bits [30:ext-CLUSTERPMU_PMCFGR.N] are
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
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wsl1733415308126__id-3-reset" rowspan="1">
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
     Event counter disable bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERPMU_PMCFGR.N is less than 31, bits [30:ext-CLUSTERPMU_PMCFGR.N] are
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
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wsl1733415308126__id-2-reset" rowspan="1">
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
     Event counter disable bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERPMU_PMCFGR.N is less than 31, bits [30:ext-CLUSTERPMU_PMCFGR.N] are
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
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wsl1733415308126__id-1-reset" rowspan="1">
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
     Event counter disable bit for ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERPMU_PMCFGR.N is less than 31, bits [30:ext-CLUSTERPMU_PMCFGR.N] are
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
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERPMU_PMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="wsl1733415308126__id-0-reset" rowspan="1">
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
