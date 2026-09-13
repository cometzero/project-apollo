# External cluster AMU registers

Source: <https://developer.arm.com/documentation/107721/0001/Activity-Monitors-Extension-support/External-cluster-AMU-registers>

### External cluster AMU registers

The cluster Activity Monitor Unit (AMU) registers are only accessible from memory-mapped accesses on the utility bus.

The summary table provides an overview of all the cluster AMU registers that are accessed externally (memory-mapped) from the utility bus of the DSU-120AE. For more information about a register, click on the register name in the table. For more information on the architecture of the AMU registers, see  [Arm® CoreSight™ Performance Monitoring Unit Architecture](https://developer.arm.com/documentation/ihi0091/latest/).

> ### Note
>
> - The cluster AMU registers are treated as RAZ/WI if either:
>   - The register is marked as Reserved.
>   - The register is accessed in the wrong Security state.
> - Any address that is not documented is treated as RAZ/WI.
> - The part number is 0x04EA.
> - The base address for the cluster AMU registers is 0x040000.
> - For registers without a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="yte1660577318752__d410e26">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU registers summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d330933e123" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d330933e125" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d330933e127" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d330933e129" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d330933e131" rowspan="1">
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
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR0--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR0--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 0, which counts events.">
     CLUSTERAMU_AMEVCNTR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR1--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR1--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 1, which counts events.">
     CLUSTERAMU_AMEVCNTR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x10
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR2--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR2--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 2, which counts events.">
     CLUSTERAMU_AMEVCNTR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x18
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR3--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR3--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 3, which counts events.">
     CLUSTERAMU_AMEVCNTR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR4--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR4--Cluster-Activity-Monitors-Event-Count-Registers?lang=en" title="Holds event counter 4, which counts events.">
     CLUSTERAMU_AMEVCNTR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Count Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x400
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER0--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER0--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 31.">
     CLUSTERAMU_AMEVTYPER0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x404
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER1--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER1--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 31.">
     CLUSTERAMU_AMEVTYPER1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x408
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER2--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER2--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 31.">
     CLUSTERAMU_AMEVTYPER2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x40C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER3--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER3--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 31.">
     CLUSTERAMU_AMEVTYPER3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x410
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER4--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER4--Cluster-Activity-Monitors-Event-Type-Registers?lang=en" title="Configures event counter n, where n is 0 to 31.">
     CLUSTERAMU_AMEVTYPER4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Event Type Registers
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC00
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCNTENSET--Cluster-Activity-Monitors-Count-Enable-Set-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCNTENSET--Cluster-Activity-Monitors-Count-Enable-Set-register?lang=en" title="Enables the implemented event counters CLUSTERAMEVCNTR&lt;n&gt;.">
     CLUSTERAMU_AMCNTENSET
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Count Enable Set register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xC20
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCNTENCLR--Cluster-Activity-Monitors-Count-Enable-Clear-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCNTENCLR--Cluster-Activity-Monitors-Count-Enable-Clear-register?lang=en" title="Disables the implemented event counters CLUSTERAMEVCNTR&lt;n&gt;.">
     CLUSTERAMU_AMCNTENCLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Count Enable Clear register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE00
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCFGR--Cluster-Activity-Monitors-Configuration-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCFGR--Cluster-Activity-Monitors-Configuration-Register?lang=en" title="Contains AMU-specific configuration data.">
     CLUSTERAMU_AMCFGR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Configuration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE04
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCR--Cluster-Activity-Monitors-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCR--Cluster-Activity-Monitors-Control-Register?lang=en" title="Provides configuration details of the Activity Monitors implementation.">
     CLUSTERAMU_AMCR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xE08
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMIIDR--Cluster-Activity-Monitors-Implementation-Identification-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMIIDR--Cluster-Activity-Monitors-Implementation-Identification-register?lang=en" title="Defines the implemented of the component..">
     CLUSTERAMU_AMIIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Implementation Identification register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFA8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVAFF--Cluster-Activity-Monitors-Device-Affinity-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVAFF--Cluster-Activity-Monitors-Device-Affinity-register?lang=en" title="Allows the external agent to determine which PE in a multiprocessor system the Activity Monitor component relates to.">
     CLUSTERAMU_AMDEVAFF
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Device Affinity register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFBC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVARCH--Cluster-Activity-Monitors-Device-Architecture-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVARCH--Cluster-Activity-Monitors-Device-Architecture-register?lang=en" title="Identifies the programmers' model architecture of the Activity Monitor component.">
     CLUSTERAMU_AMDEVARCH
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Device Architecture register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFC8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVID--Cluster-Activity-Monitors-Device-ID-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVID--Cluster-Activity-Monitors-Device-ID-register?lang=en" title="Provides information about features of the Activity Monitors implementation.">
     CLUSTERAMU_AMDEVID
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Device ID register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFCC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVTYPE--Cluster-Activity-Monitors-Device-Type-register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVTYPE--Cluster-Activity-Monitors-Device-Type-register?lang=en" title="Indicates to a debugger that this component is part of a processor Activity monitor interface.">
     CLUSTERAMU_AMDEVTYPE
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Device Type register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR4--Cluster-Activity-Monitors-Peripheral-Identification-Register-4?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR4--Cluster-Activity-Monitors-Peripheral-Identification-Register-4?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMPIDR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Peripheral Identification Register 4
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR0--Cluster-Activity-Monitors-Peripheral-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR0--Cluster-Activity-Monitors-Peripheral-Identification-Register-0?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMPIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Peripheral Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR1--Cluster-Activity-Monitors-Peripheral-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR1--Cluster-Activity-Monitors-Peripheral-Identification-Register-1?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMPIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Peripheral Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR2--Cluster-Activity-Monitors-Peripheral-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR2--Cluster-Activity-Monitors-Peripheral-Identification-Register-2?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMPIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Peripheral Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR3--Cluster-Activity-Monitors-Peripheral-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR3--Cluster-Activity-Monitors-Peripheral-Identification-Register-3?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMPIDR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Peripheral Identification Register 3
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCIDR0--Cluster-Activity-Monitors-Component-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCIDR0--Cluster-Activity-Monitors-Component-Identification-Register-0?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMCIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Component Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCIDR1--Cluster-Activity-Monitors-Component-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCIDR1--Cluster-Activity-Monitors-Component-Identification-Register-1?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMCIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Component Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCIDR2--Cluster-Activity-Monitors-Component-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCIDR2--Cluster-Activity-Monitors-Component-Identification-Register-2?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMCIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Component Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFFC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCIDR3--Cluster-Activity-Monitors-Component-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCIDR3--Cluster-Activity-Monitors-Component-Identification-Register-3?lang=en" title="Provides information to identify a Activity Monitor component.">
     CLUSTERAMU_AMCIDR3
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cluster Activity Monitors Component Identification Register 3
   </td>
  </tr>
 </tbody>
</table>
