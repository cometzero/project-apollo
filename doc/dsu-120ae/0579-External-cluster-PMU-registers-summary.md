# External cluster PMU registers summary

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary>

### External cluster PMU registers summary

The cluster Performance Monitoring Unit (PMU) registers are accessible either from memory-mapped accesses over the debug APB interface or from System register accesses from the cores.

The summary table provides an overview of all the cluster PMU registers that are accessed externally (memory-mapped) over the debug APB bus. For more information about a register, click on the register name in the table.

> ### Note
>
> - The cluster PMU registers are treated as RAZ/WI if the register is marked Reserved.
> - Any address that is not documented is treated as RAZ/WI.
> - The part number is 0x4EA.
> - For registers without a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="ntn1733415283883__summary_table">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU registers summary
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d106790e90" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d106790e92" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d106790e94" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d106790e96" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d106790e98" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR0--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR0--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 0, which counts events.">
     CLUSTERPMU_PMEVCNTR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR1--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR1--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 1, which counts events.">
     CLUSTERPMU_PMEVCNTR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x10
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR2--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR2--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 2, which counts events.">
     CLUSTERPMU_PMEVCNTR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x18
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR3--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR3--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 3, which counts events.">
     CLUSTERPMU_PMEVCNTR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR4--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR4--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 4, which counts events.">
     CLUSTERPMU_PMEVCNTR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x28
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR5--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTR5--Cluster-Performance-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 5, which counts events.">
     CLUSTERPMU_PMEVCNTR5
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x400
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER0--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER0--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 30.">
     CLUSTERPMU_PMEVTYPER0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x404
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER1--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER1--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 30.">
     CLUSTERPMU_PMEVTYPER1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x408
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER2--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER2--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 30.">
     CLUSTERPMU_PMEVTYPER2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x40C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER3--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER3--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 30.">
     CLUSTERPMU_PMEVTYPER3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x410
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER4--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER4--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 30.">
     CLUSTERPMU_PMEVTYPER4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x414
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER5--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVTYPER5--Cluster-Performance-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 30.">
     CLUSTERPMU_PMEVTYPER5
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x600
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR0--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR0--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" title="Holds event counter 0, which counts events.">
     CLUSTERPMU_PMEVCNTSR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Snapshot Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x608
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR1--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR1--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" title="Holds event counter 1, which counts events.">
     CLUSTERPMU_PMEVCNTSR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Snapshot Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x610
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR2--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR2--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" title="Holds event counter 2, which counts events.">
     CLUSTERPMU_PMEVCNTSR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Snapshot Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x618
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR3--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR3--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" title="Holds event counter 3, which counts events.">
     CLUSTERPMU_PMEVCNTSR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Snapshot Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x620
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR4--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR4--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" title="Holds event counter 4, which counts events.">
     CLUSTERPMU_PMEVCNTSR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Snapshot Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x628
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR5--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMEVCNTSR5--Cluster-Performance-Monitors-Event-Count-Snapshot-Registers?lang=en" title="Holds event counter 5, which counts events.">
     CLUSTERPMU_PMEVCNTSR5
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Event Count Snapshot Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x638
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMSSSR--Cluster-Performance-Monitors-Snapshot-Status-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMSSSR--Cluster-Performance-Monitors-Snapshot-Status-register?lang=en" title="Holds status information about the captured counters.">
     CLUSTERPMU_PMSSSR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Snapshot Status register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x640
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMOVSSR--Cluster-Performance-Monitors-Overflow-Status-Snapshot-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMOVSSR--Cluster-Performance-Monitors-Overflow-Status-Snapshot-register?lang=en" title="Captured copy of ext-CLUSTERPMU_PMOVSR. Once captured, the value in ext-CLUSTERPMU_PMOVSSR is unaffected by writes to ext-CLUSTERPMU_PMOVSSET and ext-CLUSTERPMU_PMOVSCLR.">
     CLUSTERPMU_PMOVSSR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Overflow Status Snapshot register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC00
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCNTENSET--Cluster-Performance-Monitors-Count-Enable-Set-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCNTENSET--Cluster-Performance-Monitors-Count-Enable-Set-register?lang=en" title="Enables any implemented event counters AArch64-IMP_CLUSTERPMEVCNTR&lt;n&gt;.">
     CLUSTERPMU_PMCNTENSET
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Count Enable Set register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCNTENCLR--Cluster-Performance-Monitors-Count-Enable-Clear-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCNTENCLR--Cluster-Performance-Monitors-Count-Enable-Clear-register?lang=en" title="Disables any implemented event counters AArch64-IMP_CLUSTERPMEVCNTR&lt;n&gt;.">
     CLUSTERPMU_PMCNTENCLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Count Enable Clear register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC40
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMINTENSET--Cluster-Performance-Monitors-Interrupt-Enable-Set-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMINTENSET--Cluster-Performance-Monitors-Interrupt-Enable-Set-register?lang=en" title="Enables the generation of interrupt requests on overflows from the event counters ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.">
     CLUSTERPMU_PMINTENSET
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Interrupt Enable Set register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC60
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMINTENCLR--Cluster-Performance-Monitors-Interrupt-Enable-Clear-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMINTENCLR--Cluster-Performance-Monitors-Interrupt-Enable-Clear-register?lang=en" title="Disables the generation of interrupt requests on overflows from the event counters ext-CLUSTERPMU_PMEVCNTR&lt;n&gt;.">
     CLUSTERPMU_PMINTENCLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Interrupt Enable Clear register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC80
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMOVSCLR--Cluster-Performance-Monitors-Overflow-Flag-Status-Clear-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMOVSCLR--Cluster-Performance-Monitors-Overflow-Flag-Status-Clear-register?lang=en" title="Contains the state of the overflow bit for each of the implemented event counters AArch64-PMEVCNTR&lt;n&gt;. Writing to this register clears these bits.">
     CLUSTERPMU_PMOVSCLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Overflow Flag Status Clear register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xCC0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMOVSSET--Cluster-Performance-Monitors-Overflow-Flag-Status-Set-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMOVSSET--Cluster-Performance-Monitors-Overflow-Flag-Status-Set-register?lang=en" title="Sets the state of the overflow bit for each of the implemented event counters AArch64-PMEVCNTR&lt;n&gt;.">
     CLUSTERPMU_PMOVSSET
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Overflow Flag Status Set register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE00
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCFGR--Cluster-Performance-Monitors-Configuration-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCFGR--Cluster-Performance-Monitors-Configuration-Register?lang=en" title="Contains PMU-specific configuration data.">
     CLUSTERPMU_PMCFGR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Configuration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE04
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCR--Cluster-Performance-Monitors-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCR--Cluster-Performance-Monitors-Control-Register?lang=en" title="Provides details of the Performance Monitors implementation, including the number of counters implemented, and configures and controls the counters.">
     CLUSTERPMU_PMCR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE08
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMIIDR--Cluster-Performance-Monitors-Implementation-Identification-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMIIDR--Cluster-Performance-Monitors-Implementation-Identification-register?lang=en" title="Defines the implemented of the component..">
     CLUSTERPMU_PMIIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Implementation Identification register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID0--Cluster-Performance-Monitors-Common-Event-Identification-register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID0--Cluster-Performance-Monitors-Common-Event-Identification-register-0?lang=en" title="Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the range 0x0000 to 0x001F">
     CLUSTERPMU_PMCEID0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Common Event Identification register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE24
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID1--Cluster-Performance-Monitors-Common-Event-Identification-register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID1--Cluster-Performance-Monitors-Common-Event-Identification-register-1?lang=en" title="Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the range 0x020 to 0x03F.">
     CLUSTERPMU_PMCEID1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Common Event Identification register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE28
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID2--Cluster-Performance-Monitors-Common-Event-Identification-register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID2--Cluster-Performance-Monitors-Common-Event-Identification-register-2?lang=en" title="Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the range 0x4000 to 0x401F.">
     CLUSTERPMU_PMCEID2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Common Event Identification register 2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE2C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID3--Cluster-Performance-Monitors-Common-Event-Identification-register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCEID3--Cluster-Performance-Monitors-Common-Event-Identification-register-3?lang=en" title="Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the range 0x4020 to 0x403F.">
     CLUSTERPMU_PMCEID3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Common Event Identification register 3
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE30
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMSSCR--Cluster-Performance-Monitors-Snapshot-Capture-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMSSCR--Cluster-Performance-Monitors-Snapshot-Capture-register?lang=en" title="Provides a mechanism for software to initiate a sample.">
     CLUSTERPMU_PMSSCR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Snapshot Capture register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE38
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMSSRR--Cluster-Performance-Monitors-Snapshot-Reset-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMSSRR--Cluster-Performance-Monitors-Snapshot-Reset-register?lang=en" title="Configure PMU Snapshot to reset counters after each sample taken.">
     CLUSTERPMU_PMSSRR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Snapshot Reset register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFA8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVAFF0--Cluster-Performance-Monitors-Device-Affinity-register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVAFF0--Cluster-Performance-Monitors-Device-Affinity-register-0?lang=en" title="Allows a debugger to determine which PE in a multiprocessor system the Performance Monitor component relates to.">
     CLUSTERPMU_PMDEVAFF0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Device Affinity register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFAC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVAFF1--Cluster-Performance-Monitors-Device-Affinity-register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVAFF1--Cluster-Performance-Monitors-Device-Affinity-register-1?lang=en" title="Allows a debugger to determine which PE in a multiprocessor system the Performance Monitor component relates to.">
     CLUSTERPMU_PMDEVAFF1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Device Affinity register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFB8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMAUTHSTATUS--Cluster-Performance-Monitors-Authentication-Status-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMAUTHSTATUS--Cluster-Performance-Monitors-Authentication-Status-register?lang=en" title="Provides information about the state of the authentication interface for Performance Monitors.">
     CLUSTERPMU_PMAUTHSTATUS
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Authentication Status register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFBC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVARCH--Cluster-Performance-Monitors-Device-Architecture-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVARCH--Cluster-Performance-Monitors-Device-Architecture-register?lang=en" title="Identifies the programmers' model architecture of the Performance Monitor component.">
     CLUSTERPMU_PMDEVARCH
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Device Architecture register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFC8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVID--Cluster-Performance-Monitors-Device-ID-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVID--Cluster-Performance-Monitors-Device-ID-register?lang=en" title="Provides information about features of the Performance Monitors implementation.">
     CLUSTERPMU_PMDEVID
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Device ID register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFCC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVTYPE--Cluster-Performance-Monitors-Device-Type-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMDEVTYPE--Cluster-Performance-Monitors-Device-Type-register?lang=en" title="Indicates to a debugger that this component is part of a processor performance monitor interface.">
     CLUSTERPMU_PMDEVTYPE
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Device Type register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR4--Cluster-Performance-Monitors-Peripheral-Identification-Register-4?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR4--Cluster-Performance-Monitors-Peripheral-Identification-Register-4?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMPIDR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Peripheral Identification Register 4
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR0--Cluster-Performance-Monitors-Peripheral-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR0--Cluster-Performance-Monitors-Peripheral-Identification-Register-0?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMPIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Peripheral Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR1--Cluster-Performance-Monitors-Peripheral-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR1--Cluster-Performance-Monitors-Peripheral-Identification-Register-1?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMPIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Peripheral Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR2--Cluster-Performance-Monitors-Peripheral-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR2--Cluster-Performance-Monitors-Peripheral-Identification-Register-2?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMPIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Peripheral Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR3--Cluster-Performance-Monitors-Peripheral-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMPIDR3--Cluster-Performance-Monitors-Peripheral-Identification-Register-3?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMPIDR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Peripheral Identification Register 3
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR0--Cluster-Performance-Monitors-Component-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR0--Cluster-Performance-Monitors-Component-Identification-Register-0?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMCIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Component Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR1--Cluster-Performance-Monitors-Component-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR1--Cluster-Performance-Monitors-Component-Identification-Register-1?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMCIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Component Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR2--Cluster-Performance-Monitors-Component-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR2--Cluster-Performance-Monitors-Component-Identification-Register-2?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMCIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Component Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFFC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR3--Cluster-Performance-Monitors-Component-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMCIDR3--Cluster-Performance-Monitors-Component-Identification-Register-3?lang=en" title="Provides information to identify a Performance Monitor component.">
     CLUSTERPMU_PMCIDR3
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cluster Performance Monitors Component Identification Register 3
   </td>
  </tr>
 </tbody>
</table>
