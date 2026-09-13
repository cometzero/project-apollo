# Base addresses for system-accessible components

Source: <https://developer.arm.com/documentation/107721/0001/Utility-bus/Base-addresses-for-system-accessible-components>

### Base addresses for system-accessible components

Each set of System registers is grouped on separate 64 KB page boundaries allowing access to be enforced by a Memory Management Unit (MMU).

The following table shows the base addresses for each set of registers for system-accessible components and what Security state they should be accessed from.

> ### Note
>
> - The base address for each set of registers for the core Power Policy Units (PPUs) depends on the core instance number <n>, from 0 to CN.
> - In the following table, any address space that is not documented is treated as RAZ/WI.
> - For base addresses of core registers, which are mapped from 0x<n>90000 - 0x<n>F0000, see your core Technical Reference Manual (TRM).
> - The base addresses in the following table are the addresses accessed on the utility bus interface. The system interconnect typically maps these addresses into a particular address range based on the system address map. Therefore, software has to add the base address listed here onto the system address range base to get the absolute physical address of a register.

<table id="ryl1660577298593__table_system_components_util_bus_ae">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Utility bus base addresses for system-accessible component registers
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
   <th class="documents-nocellnorowborder" colspan="1" id="d271185e117" rowspan="1">
    Base address, n is core instance number
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d271185e120" rowspan="1">
    Registers
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d271185e123" rowspan="1">
    Security state
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d271185e126" rowspan="1">
    Memory map
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x000000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster control
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Secure state
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary?lang=en" title="The cluster system control registers are accessible either from memory-mapped accesses on the utility bus or from System register accesses from the cores.">
     External cluster system control registers summary
    </a>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x010000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster MPAM
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Any state
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary?lang=en" title="The cluster Memory System Resource Partitioning and Monitoring (MPAM) registers are only accessible from memory-mapped accesses on the utility bus.">
     External MPAM registers summary
    </a>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x020000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster RAS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Secure state
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary?lang=en" title="The cluster RAS registers are accessible either from memory-mapped accesses on the utility bus or from System register accesses from the cores.">
     External cluster RAS registers summary
    </a>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x030000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster PPU
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Secure state
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-PPU-registers-summary?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-PPU-registers-summary?lang=en" title="The Power Policy Unit (PPU) registers for the DSU-120AE DynamIQ cluster are only accessible from memory-mapped accesses on the utility bus.">
     External cluster PPU registers summary
    </a>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x040000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Activity Monitors
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Secure state
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary?lang=en" title="The cluster Activity Monitor Unit (AMU) registers are only accessible from memory-mapped accesses on the utility bus.">
     External cluster AMU registers summary
    </a>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x050000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cluster AE registers
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Secure state
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary?lang=en" title="The cluster Automotive Enhanced (AE) registers are only accessible from memory-mapped accesses on the utility bus.">
     External cluster AE registers summary
    </a>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x060000
    </span>
    -
    <span class="documents-g.number.hex">
     0x070000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved for future cluster registers
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x&lt;n&gt;80000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    &lt;n&gt; PPU
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Secure state
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary?lang=en" title="Each core Power Policy Unit (PPU) in the DSU-120AE DynamIQ cluster has an individual set of Power Policy Unit (PPU) registers. Each set of registers is identical, and are memory-mapped onto the utility bus at different base addresses.">
     External core PPU registers summary
    </a>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x&lt;n&gt;90000
    </span>
    -
    <span class="documents-g.number.hex">
     0x&lt;n&gt;F0000
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    &lt;n&gt; registers
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See your
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    TRM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    See your
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    TRM
   </td>
  </tr>
 </tbody>
</table>
