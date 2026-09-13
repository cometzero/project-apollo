# AArch64 generic system control registers summary

Source: <https://developer.arm.com/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary>

### AArch64 generic system control registers summary

The cluster Generic System Control registers are accessible either from System register accesses from the cores or from memory-mapped accesses on the utility bus.

The summary table provides an overview of all the AArch64 Generic System Control registers in the DSU-120AE. For more information about a register, click on the register name in the table.

> ### Note
>
> For registers with a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="afu1733414813960__summary_table">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Generic System Control registers summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d197259e82" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d197259e84" rowspan="1">
    Op0
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d197259e86" rowspan="1">
    Op1
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d197259e88" rowspan="1">
    CRn
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d197259e90" rowspan="1">
    CRm
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d197259e92" rowspan="1">
    Op2
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d197259e94" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d197259e96" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d197259e98" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCFR-EL1--Cluster-Configuration-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCFR-EL1--Cluster-Configuration-Register?lang=en" title="Contains details of the hardware configuration of the cluster.">
     IMP_CLUSTERCFR_EL1
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
    C3
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
    Cluster Configuration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERIDR-EL1--Cluster-Main-Revision-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERIDR-EL1--Cluster-Main-Revision-Register?lang=en" title="Holds the revision and patch level of the cluster.">
     IMP_CLUSTERIDR_EL1
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
    C3
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
    Cluster Main Revision Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERREVIDR-EL1--Cluster-ECO-ID-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERREVIDR-EL1--Cluster-ECO-ID-Register?lang=en" title="Enables ECO patches to be applied to the cluster-level to be identified by software.">
     IMP_CLUSTERREVIDR_EL1
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
    C3
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
    Cluster ECO ID Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERACTLR-EL1--Cluster-Auxiliary-Control-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERACTLR-EL1--Cluster-Auxiliary-Control-Register?lang=en" title="These register bits are reserved for Arm test purposes only and must not be used except under direction from Arm.">
     IMP_CLUSTERACTLR_EL1
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
    C3
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
    Cluster Auxiliary Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERECTLR-EL1--Cluster-Extended-Control-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERECTLR-EL1--Cluster-Extended-Control-Register?lang=en" title="This register should be used for dynamically changing implementation specific control bits.">
     IMP_CLUSTERECTLR_EL1
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
    C3
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
    Cluster Extended Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRCTLR-EL1--Cluster-Power-Control-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRCTLR-EL1--Cluster-Power-Control-Register?lang=en" title="This register controls power features of the cluster.">
     IMP_CLUSTERPWRCTLR_EL1
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
    C3
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
    Cluster Power Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRDN-EL1--Cluster-Power-Down-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRDN-EL1--Cluster-Power-Down-Register?lang=en" title="This register controls powerdown requirements of the cluster and is banked per-thread.">
     IMP_CLUSTERPWRDN_EL1
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
    C3
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
    Cluster Power Down Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRSTAT-EL1--Cluster-Power-Status-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRSTAT-EL1--Cluster-Power-Status-Register?lang=en" title="This register contains the current status of power features and is read-only.">
     IMP_CLUSTERPWRSTAT_EL1
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
    C3
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
    Cluster Power Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3DNTH0-EL1--Cluster-L3-Downsize-Threshold0-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3DNTH0-EL1--Cluster-L3-Downsize-Threshold0-Register?lang=en" title="This register is intended for use in algorithms for determining when to power up or down cache portions.">
     IMP_CLUSTERL3DNTH0_EL1
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
    C4
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
    Cluster L3 Downsize Threshold0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3DNTH1-EL1--Cluster-L3-Downsize-Threshold1-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3DNTH1-EL1--Cluster-L3-Downsize-Threshold1-Register?lang=en" title="This register is intended for use in algorithms for determining when to power up or down cache portions.">
     IMP_CLUSTERL3DNTH1_EL1
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
    C4
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
    Cluster L3 Downsize Threshold1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3UPTH0-EL1--Cluster-L3-Upsize-Threshold0-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3UPTH0-EL1--Cluster-L3-Upsize-Threshold0-Register?lang=en" title="This register is intended for use in algorithms for determining when to power up or down cache portions.">
     IMP_CLUSTERL3UPTH0_EL1
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
    C4
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
    Cluster L3 Upsize Threshold0 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3UPTH1-EL1--Cluster-L3-Upsize-Threshold1-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3UPTH1-EL1--Cluster-L3-Upsize-Threshold1-Register?lang=en" title="This register is intended for use in algorithms for determining when to power up or down cache portions.">
     IMP_CLUSTERL3UPTH1_EL1
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
    C4
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
    Cluster L3 Upsize Threshold1 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERBUSQOS-EL1--Cluster-Bus-QoS-Control-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERBUSQOS-EL1--Cluster-Bus-QoS-Control-Register?lang=en" title="Determines the value driven on the CHI bus QoS field.">
     IMP_CLUSTERBUSQOS_EL1
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
    C4
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
    Cluster Bus QoS Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3HIT-EL1--Cluster-L3-Hit-Counter-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3HIT-EL1--Cluster-L3-Hit-Counter-Register?lang=en" title="This register is intended for use in algorithms for determining when to power up or down cache portions.">
     IMP_CLUSTERL3HIT_EL1
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
    C4
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
    Cluster L3 Hit Counter Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3MISS-EL1--Cluster-L3-Miss-Counter-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3MISS-EL1--Cluster-L3-Miss-Counter-Register?lang=en" title="This register is intended for use in algorithms for determining when to power up or down cache portions.">
     IMP_CLUSTERL3MISS_EL1
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
    C4
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
    Cluster L3 Miss Counter Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPPSTART-EL1--Cluster-Peripheral-Port-Start-Address-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPPSTART-EL1--Cluster-Peripheral-Port-Start-Address-Register?lang=en" title="Determines the start address for the peripheral port address range.">
     IMP_CLUSTERPPSTART_EL1
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
    C9
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
    Cluster Peripheral Port Start Address Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPPEND-EL1--Cluster-Peripheral-Port-End-Address-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPPEND-EL1--Cluster-Peripheral-Port-End-Address-Register?lang=en" title="Determines the end address for the peripheral port address range.">
     IMP_CLUSTERPPEND_EL1
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
    C9
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
    Cluster Peripheral Port End Address Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCFR2-EL1--Cluster-Configuration-Register-2?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCFR2-EL1--Cluster-Configuration-Register-2?lang=en" title="Contains details of the hardware configuration of the cluster.">
     IMP_CLUSTERCFR2_EL1
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
    C9
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
    Cluster Configuration Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3UPTH2-EL1--Cluster-L3-Upsize-Threshold2-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERL3UPTH2-EL1--Cluster-L3-Upsize-Threshold2-Register?lang=en" title="This register is intended for use in algorithms for determining when to power up slices.">
     IMP_CLUSTERL3UPTH2_EL1
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
    C9
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
    Cluster L3 Upsize Threshold2 Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCDBG-EL3--Cluster-Cache-Debug-Register?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERCDBG-EL3--Cluster-Cache-Debug-Register?lang=en" title="Can be used to read the contents of the L3 cache RAMs and snoop filter RAMs. The register must be written with the information of which RAM is to be read. Then the same register should be read to read the contents of that RAM.">
     IMP_CLUSTERCDBG_EL3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    C4
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
    Cluster Cache Debug Register
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPMMDCR-EL3--Monitor-Debug-Configuration-Register--EL3-?lang=en" href="/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPMMDCR-EL3--Monitor-Debug-Configuration-Register--EL3-?lang=en" title="Provides EL3 configuration options for self-hosted debug and the Performance Monitors Extension.">
     IMP_CLUSTERPMMDCR_EL3
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    6
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    C15
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    C6
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Monitor Debug Configuration Register (EL3)
   </td>
  </tr>
 </tbody>
</table>
