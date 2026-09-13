# Debug system address map

Source: <https://developer.arm.com/documentation/107721/0001/ROM-tables/Debug-system-address-map>

### Debug system address map

The debug system address map for the DynamIQ Shared Unit-120AE (DSU-120AE) cluster depends on the specific implementation of your cluster, for example the number of cores configured in the cluster.

The following describes the conditions for certain entries being present in the address map:

Core or Complex <n> ROM tables:
:   Where n is the core instance number. These entries point to the ROM tables for a core or a complex. A complex only contains a single ROM table and so a ROM table is not present for cores that form the second core of a dual core complex. The single ROM table that is included in a dual core complex contains the addresses for both of the cores in the dual core complex.

    The addresses for any component in a core instance, for example Performance Monitoring Unit (PMU) and Embedded Trace Extension (ETE), are the same irrespective of whether the core instance is a standalone core, a single core complex, or part of a dual core complex. However, the ROM table hierarchy that is used to identify the address values differ depending on the configuration.

Cluster ELA
:   These entries are only present if the Embedded Logic Analyzer (ELA) is included in the cluster.

Core ELAs
:   These entries are only present if the ELA is included in the
    core or
    complex. When an ELA is included in a dual
    core
    complex, there is only one ELA present. The ELA is located after the ETE for the first
    core of the
    complex.

Components
:   Components are only present for
    cores that are included in the cluster.

### Debug APB system address map

The following table shows the debug system address map for the DSU-120AE DynamIQ™ cluster.

<table id="mvs1660577310746__table_er3_5kq_qmb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Debug APB system address map
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d319076e261" rowspan="1">
    Debug component (if present)
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d319076e264" rowspan="1">
    Debug APB address offset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DebugBlock ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x10000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x20000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x30000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x40000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    0 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x80000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    0 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x90000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    0 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xA0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    0 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xB0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    0 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xC0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    0 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xF0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    1 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x100000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    1 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x110000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    1 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x120000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    1 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x130000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    1 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x140000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    1 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x170000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    2 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x180000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    2 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x190000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    2 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1A0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    2 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1B0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    2 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1C0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    2 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1F0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    3 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x200000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    3 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x210000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    3 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x220000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    3 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x230000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    3 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x240000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    3 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x270000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    4 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x280000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    4 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x290000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    4 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2A0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    4 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2B0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    4 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2C0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    4 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2F0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    5 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x300000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    5 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x310000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    5 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x320000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    5 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x330000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    5 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x340000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    5 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x370000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    6 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x380000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    6 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x390000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    6 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3A0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    6 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3B0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    6 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3C0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    6 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3F0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    7 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x400000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    7 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x410000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    7 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x420000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    7 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x430000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    7 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x440000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    7 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x470000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    8 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x480000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    8 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x490000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    8 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4A0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    8 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4B0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    8 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4C0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    8 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4F0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    9 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x500000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    9 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x510000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    9 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x520000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    9 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x530000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    9 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x540000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    9 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x570000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    10 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x580000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    10 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x590000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    10 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5A0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    10 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5B0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    10 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5C0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    10 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5F0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    11 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x600000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    11 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x610000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    11 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x620000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    11 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x630000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    11 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x640000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    11 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x670000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    12 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x680000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    12 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x690000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    12 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x6A0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    12 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x6B0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    12 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x6C0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    12 CTI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x6F0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Complex
    </span>
    or
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    13 ROM Table
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x700000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    13 Debug
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x710000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    13 PMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x720000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    13 ETE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x730000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    13 ELA
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x740000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    13 CTI
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x770000
    </span>
   </td>
  </tr>
 </tbody>
</table>
