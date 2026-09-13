# CLUSTERPMU_PMCFGR, Cluster Performance Monitors Configuration Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCFGR--Cluster-Performance-Monitors-Configuration-Register>

### CLUSTERPMU\_PMCFGR, Cluster Performance Monitors Configuration Register

Contains PMU-specific configuration data.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xE00

Access type
:   See bit descriptions

Reset value
:   ```
    xxxx xxxx x11x 0xx0 0011 1111 0000 0101
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterpmu\_pmcfgr bit assignments

![ext_clusterpmu_pmcfgr bit assignments](images/0606-CLUSTERPMU_PMCFGR-Cluster-Performance-Monitors-Configuration-Register-img01.svg)

<table id="hef1733415315568__aclusterpmu_pmcfgr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMCFGR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d208838e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d208838e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d208838e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d208838e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:23]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__31-23-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [22]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Snapshot supported.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Snapshot supported.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__id-22-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [21]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FZO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Freeze on overflow supported.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Freeze on overflow supported.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__id-21-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__20-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    UEN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     User-mode Enable Register supported.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       User-mode Enable Register not supported.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__id-19-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [18:17]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__18-17-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    EX
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Export supported.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERPMU_PMCR.X is
       <span class="documents-archterm">
        RES0
       </span>
       .
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__id-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CCD
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Cycle counter has prescale.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERPMU_PMCR.D is
       <span class="documents-archterm">
        RES0
       </span>
       .
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__id-15-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [14]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Dedicated cycle counter.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Dedicated cycle counter ext-CLUSTERPMU_PMCCNTR is not supported.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__id-14-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [13:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SIZE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Size of counters, minus one. This field defines the size of the largest counter implemented by the Performance Monitors Unit.
    </p>
    <p>
     This field is used by software to determine the spacing of the counters in the memory-map.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111111
      </span>
     </dt>
     <dd>
      <p>
       The largest counter is 64-bits. Counters are at doubleword-aligned addresses.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hef1733415315568__id-13-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b111111
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    N
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of counters implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000101
      </span>
     </dt>
     <dd>
      <p>
       Six event counters implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="hef1733415315568__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x05
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

When IsCorePowered() && !DoubleLockStatus() && !OSLockStatus() && AllowExternalPMUAccess()
:   RO

Otherwise
:   ERROR
