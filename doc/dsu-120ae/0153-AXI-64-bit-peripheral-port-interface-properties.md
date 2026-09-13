# AXI 64-bit peripheral port interface properties

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/AXI-64-bit-peripheral-port-interface-properties>

### AXI 64-bit peripheral port interface properties

AMBA defines a set of interface properties for the AXI interconnect. The AXI 64-bit configured peripheral port of the DynamIQ Shared Unit-120AE (DSU-120AE) only supports some of these interface properties.

The following table shows which AXI interface properties the AXI 64-bit configured peripheral port supports, and if interconnect or system support is required. You must ensure that your system interconnect, where applicable, supports these properties.

<table id="ows1660577283059__table_w3786ab1b9b1b3_w3787ab1b9b1_w3788ab1b9_w3789ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   AXI 64-bit peripheral port interface properties
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d186784e72" rowspan="1">
    AXI property
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d186784e75" rowspan="1">
    Supported by the
    <span class="documents-keyword">
     DSU-120AE
    </span>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d186784e80" rowspan="1">
    Interconnect or system support required
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Continuous_Cache_Line_Read_Data
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Multi_Copy_Atomicity
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Ordered_Write_Observation
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WriteEvict_Transaction
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DVM_v8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Atomic_Transactions
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Optional, to send atomics to the interconnect set the
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTATOMICMP
     </span>
    </span>
    signal HIGH.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DVM_v8.1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cache_Stash_Transactions
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DeAllocation_Transactions
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Persist_CMO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Poison
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Check_Type
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    QoS_Accept
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Trace_Signals
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Loopback_Signals
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Wakeup_Signals
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Untranslated_Transactions
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NSAccess_Identifiers
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Coherency_Connection_Signals
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Barrier_Transactions
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MPAM_Support
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes, the
    <span class="documents-keyword">
     DSU-120AE
    </span>
    cluster supports MPAM_6_1
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Optional
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Unique_ID_Support
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Read_Interleaving_Disabled
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Partial_Read_Data
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Read_Data_Reordering
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WriteCMO_Transactions
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MTE_Support
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Not applicable
   </td>
  </tr>
 </tbody>
</table>
