# ACP features

Source: <https://developer.arm.com/documentation/107721/0001/ACP-subordinate-interface/ACP-features>

### ACP features

The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification and includes support for atomic transactions and cache stashing. Memory tagging is also supported but only to a basic level as defined by the AMBA specification. This allows reading and writing the tags but does not support tag matching on writes.

> ### Note
>
> See
>  [AMBA® AXI Protocol Specification](https://developer.arm.com/documentation/ihi0022/latest/) for a description of the AMBA ACE5-LiteDVM protocol.

The following table shows the ACP interface properties that are supported by the DynamIQ Shared Unit-120AE (DSU-120AE).

<table id="xdp1660577277934__table_w3625ab1b9b1b5_w3626ab1b9b1_w3627ab1b9_w3628ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   ACP interface properties for the
   <span class="documents-keyword">
    DSU-120AE
   </span>
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d372028e92" rowspan="1">
    ACP property
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d372028e95" rowspan="1">
    Supported by the
    <span class="documents-keyword">
     DSU-120AE
    </span>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Port_Type
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Accelerator
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Continuous_Cache_Line_Read_Data
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Multi_Copy_Atomicity
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes. System support is required.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Ordered_Write_Observation
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
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_v8
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Atomic_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_v8.1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_v8.4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cache_Stash_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Prefetch_Transactions
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
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Persistent_CMO
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Write_Plus_CMO
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
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Data_Check
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
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Trace_Signals
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
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Low_Power_Signals
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Untranslated_Transactions
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
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WriteZero_Transaction
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Regular_Transactions_Only
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Only regular transactions are supported.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Exclusive_Accesses
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
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Max_Transaction_Bytes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    64
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_Message_Support
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Receiver
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MPAM_Support
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MTE_Support
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    If the
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTMTE
     </span>
    </span>
    signal is
    <code>
     HIGH
    </code>
    , Standard support is provided. If the
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTMTE
     </span>
    </span>
    signal is
    <code>
     LOW
    </code>
    , no support is provided.
   </td>
  </tr>
 </tbody>
</table>

### Related information

- [ACP ACE5-LiteDVM protocol subset](/documentation/107721/0001/ACP-subordinate-interface/ACP-ACE5-LiteDVM-protocol-subset?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification that includes support for Cacheable, Non-cacheable, and Device memory accesses.")
- [ACP transactions](/documentation/107721/0001/ACP-subordinate-interface/ACP-transactions?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification. The ACP interface includes support for Cacheable, Non-cacheable, Device, and Atomic memory accesses.")
