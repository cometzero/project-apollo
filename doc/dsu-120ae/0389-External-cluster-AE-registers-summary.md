# External cluster AE registers summary

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary>

### External cluster AE registers summary

The cluster Automotive Enhanced (AE) registers are only accessible from memory-mapped accesses on the utility bus.

The summary table provides an overview of all the cluster AE registers that are accessed externally (memory-mapped) from the utility bus of the DSU-120AE. For more information about a register, click on the register name in the table.

> ### Note
>
> - The cluster AE registers are treated as RAZ/WI if either:
>   - The register is marked as Reserved.
>   - The register is accessed in the wrong Security state.
> - Any address that is not documented is treated as RAZ/WI.
> - The base address for the cluster AE registers is 0x050000.
> - For registers without a listed reset value refer to the individual field resets documented on the register description pages.

<table class="documents-opcodes" id="xll1733415031315__summary_table">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAE registers summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d238110e97" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d238110e99" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d238110e101" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d238110e103" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d238110e105" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERSLCFR--Cluster-Split-Lock-Configuration-Feature-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERSLCFR--Cluster-Split-Lock-Configuration-Feature-Register?lang=en" title="Describes the supported AE features of the Cluster and Cores.">
     CLUSTERAE_CLUSTERSLCFR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Split/Lock Configuration Feature Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0008
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERSLCTLR--Cluster-Split-Lock-Configuration-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERSLCTLR--Cluster-Split-Lock-Configuration-Control-Register?lang=en" title="Control register for setting the Split/Lock mode of the Cluster.">
     CLUSTERAE_CLUSTERSLCTLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Split/Lock Configuration Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERSLSTAT--Cluster-Split-Lock-Configuration-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERSLSTAT--Cluster-Split-Lock-Configuration-Status-Register?lang=en" title="Status register describing power and operating status of cluster and cores.">
     CLUSTERAE_CLUSTERSLSTAT
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Split/Lock Configuration Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CORESLCFR--Core-Split-Lock-Configuration-Feature-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CORESLCFR--Core-Split-Lock-Configuration-Feature-Register?lang=en" title="Describes supported AE features of the cores.">
     CLUSTERAE_CORESLCFR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core Split/Lock Configuration Feature Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0030
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CORESLCTLR--Core-Split-Lock-Configuration-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CORESLCTLR--Core-Split-Lock-Configuration-Control-Register?lang=en" title="Control register for setting the Split/Lock mode of each core.">
     CLUSTERAE_CORESLCTLR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core Split/Lock Configuration Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0040
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CORESLSTAT--Core-Split-Lock-Configuration-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CORESLSTAT--Core-Split-Lock-Configuration-Status-Register?lang=en" title="Status register showing power and operating status of each core.">
     CLUSTERAE_CORESLSTAT
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core Split/Lock Configuration Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x0050
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERRECOV--Cluster-Recovery-Control-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERRECOV--Cluster-Recovery-Control-Register?lang=en" title="Debug recovery and warm reset request register.">
     CLUSTERAE_CLUSTERRECOV
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster Recovery Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0060
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERWRITEKEY--Cluster-Write-Key-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AE-registers-summary/CLUSTERAE-CLUSTERWRITEKEY--Cluster-Write-Key-Register?lang=en" title="Control register for setting the Cluster KEY to enable writing of AE and PPU registers.">
     CLUSTERAE_CLUSTERWRITEKEY
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    64-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cluster Write Key Register
   </td>
  </tr>
 </tbody>
</table>
