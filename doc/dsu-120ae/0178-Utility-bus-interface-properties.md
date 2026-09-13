# Utility bus interface properties

Source: <https://developer.arm.com/documentation/107721/0001/Utility-bus/Utility-bus-interface-properties>

### Utility bus interface properties

The DSU-120AE utility bus is implemented as a 64-bit AMBA AXI5 subordinate port. AMBA defines a set of properties for AXI for which the utility bus only supports a subset of these.

The following table shows which AXI properties the utility bus supports.

<table id="jca1746715100905__table_w327ab1b7b1b3_w328ab1b7b1_w329ab1b7_w330ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   AXI interconnect properties for the utility bus
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d188771e67" rowspan="1">
    AXI property
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d188771e70" rowspan="1">
    Supported by the utility bus
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d188771e73" rowspan="1">
    Interconnect or system support required
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Atomic_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Barrier_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cache_Stash_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Check_Type
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    CMO_On_Read
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    CMO_On_Write
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Coherency_Connection_Signals
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DeAllocation_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_Message_Support
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_v8
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_v8.1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_v8.4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Exclusive_Accesses
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Loopback_Signals
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Max_Transaction_Bytes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    64
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MPAM_Support
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MTE_Support
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Multi_Copy_Atomicity
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    NSAccess_Identifiers
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Ordered_Write_Observation
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Persist_CMO
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Poison
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Prefetch_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    QoS_Accept
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Read_Interleaving_Disabled
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Shareable_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Trace_Signals
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Unique_ID_Support
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Untranslated_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Wakeup_Signals
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Write_Plus_CMO
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WriteEvict_Transaction
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WriteZero_Transaction
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
 </tbody>
</table>
