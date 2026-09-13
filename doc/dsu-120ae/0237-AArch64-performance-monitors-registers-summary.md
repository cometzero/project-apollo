# AArch64 performance monitors registers summary

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary>

### AArch64 performance monitors registers summary

The cluster Performance Monitors registers are accessible either from System register accesses from the cores or from memory-mapped accesses on the utility bus.

The summary table provides an overview of all AArch64 cluster Performance Monitors registers in the DSU-120AE. For more information about a register, click on the register name in the table.

> ### Note
>
> - For registers without a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="cgg1733414874962__summary_table">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Performance Monitors registers summary
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d321414e85" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d321414e87" rowspan="1">
    Op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d321414e89" rowspan="1">
    Op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d321414e91" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d321414e93" rowspan="1">
    CRm
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d321414e95" rowspan="1">
    Op2
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d321414e97" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d321414e99" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d321414e101" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCR-EL1--Performance-Monitors-Control-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCR-EL1--Performance-Monitors-Control-Register?lang=en" title="Provides details of the Performance Monitors implementation, including the number of counters implemented, and configures and controls the counters.">
     IMP_CLUSTERPMCR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCNTENSET-EL1--Performance-Monitors-Count-Enable-Set-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCNTENSET-EL1--Performance-Monitors-Count-Enable-Set-Register?lang=en" title="Enables all implemented event counters AArch64-IMP_CLUSTERPMXEVCNTR_EL1.">
     IMP_CLUSTERPMCNTENSET_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Count Enable Set Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCNTENCLR-EL1--Performance-Monitors-Count-Enable-Clear-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCNTENCLR-EL1--Performance-Monitors-Count-Enable-Clear-Register?lang=en" title="Disables all implemented event counters AArch64-IMP_CLUSTERPMXEVCNTR_EL1.">
     IMP_CLUSTERPMCNTENCLR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Count Enable Clear Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMOVSSET-EL1--Performance-Monitors-Overflow-Flag-Status-Set-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMOVSSET-EL1--Performance-Monitors-Overflow-Flag-Status-Set-Register?lang=en" title="Sets the state of the overflow bit for each of the implemented event counters AArch64-PMXEVCNTR_EL1.">
     IMP_CLUSTERPMOVSSET_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Overflow Flag Status Set Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMOVSCLR-EL1--Performance-Monitors-Overflow-Flag-Status-Clear-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMOVSCLR-EL1--Performance-Monitors-Overflow-Flag-Status-Clear-Register?lang=en" title="Contains the state of the overflow bit for each of the implemented event counters AArch64-PMXEVCNTR_EL1. Writing to this register clears these bits.">
     IMP_CLUSTERPMOVSCLR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Overflow Flag Status Clear Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMSELR-EL1--Performance-Monitors-Event-Counter-Selection-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMSELR-EL1--Performance-Monitors-Event-Counter-Selection-Register?lang=en" title="Selects the current event counter AArch64-IMP_CLUSTERPMEVCNTR_EL1.">
     IMP_CLUSTERPMSELR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Event Counter Selection Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMINTENSET-EL1--Performance-Monitors-Interrupt-Enable-Set-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMINTENSET-EL1--Performance-Monitors-Interrupt-Enable-Set-Register?lang=en" title="Enables the generation of interrupt requests on overflows from the event counters AArch64-IMP_CLUSTERPMXEVCNTR_EL1.">
     IMP_CLUSTERPMINTENSET_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Interrupt Enable Set Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMINTENCLR-EL1--Performance-Monitors-Interrupt-Enable-Clear-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMINTENCLR-EL1--Performance-Monitors-Interrupt-Enable-Clear-Register?lang=en" title="Disables the generation of interrupt requests on overflows from the event counters AArch64-IMP_CLUSTERPMXEVCNTR_EL1.">
     IMP_CLUSTERPMINTENCLR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Interrupt Enable Clear Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCCNTR-EL1--Performance-Monitors-Cycle-Count-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCCNTR-EL1--Performance-Monitors-Cycle-Count-Register?lang=en" title="Holds the value of the processor Cycle Counter, CCNT, that counts processor clock cycles. RES0 if not implemented.">
     IMP_CLUSTERPMCCNTR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Cycle Count Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMXEVTYPER-EL1--Performance-Monitors-Selected-Event-Type-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMXEVTYPER-EL1--Performance-Monitors-Selected-Event-Type-Register?lang=en" title="When AArch64-IMP_CLUSTERPMSELR_EL1.SEL selects an event counter, this accesses a AArch64-IMP_CLUSTERPMXEVTYPER_EL1 register.">
     IMP_CLUSTERPMXEVTYPER_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Selected Event Type Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMXEVCNTR-EL1--Performance-Monitors-Selected-Event-Count-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMXEVCNTR-EL1--Performance-Monitors-Selected-Event-Count-Register?lang=en" title="Reads or writes the value of the selected event counter, AArch64-IMP_CLUSTERPMXEVCNTR_EL1. AArch64-IMP_CLUSTERPMSELR_EL1.SEL determines which event counter is selected.">
     IMP_CLUSTERPMXEVCNTR_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Selected Event Count Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCEID0-EL1--Performance-Monitors-Common-Event-Identification-Register-0?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCEID0-EL1--Performance-Monitors-Common-Event-Identification-Register-0?lang=en" title="Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the ranges 0x0000 to 0x001F and 0x4000 to 0x401F.">
     IMP_CLUSTERPMCEID0_EL1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Performance Monitors Common Event Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCEID1-EL1--Performance-Monitors-Common-Event-Identification-Register-1?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-performance-monitors-registers-summary/IMP-CLUSTERPMCEID1-EL1--Performance-Monitors-Common-Event-Identification-Register-1?lang=en" title="Defines which common architectural events and common microarchitectural events are implemented, or counted, using PMU events in the ranges 0x0020 to 0x003F and 0x4020 to 0x403F.">
     IMP_CLUSTERPMCEID1_EL1
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    C6
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    5
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Performance Monitors Common Event Identification Register 1
   </td>
  </tr>
 </tbody>
</table>
