# ACP performance

Source: <https://developer.arm.com/documentation/107721/0001/ACP-subordinate-interface/ACP-performance>

### ACP performance

For optimum performance, use the following guidelines for Accelerator Coherency Port (ACP) transactions.

### AXI ID guidelines

The ACP manager must avoid sending more than one outstanding transaction on the same AXI ID to prevent the second transaction stalling the interface until the first has completed. If the manager requires explicit ordering between two transactions, Arm recommends that it waits for the response to the first transaction before sending the second transaction.

### Write transactions

Writes to memory that use either WriteUniqueFull or WriteUniqueFullStash transactions have higher performance than other types of write transactions.

WriteUniquePtl or WriteUniquePtlStash transactions always incur a read-modify write sequence.

Write transactions use the Write-Allocate bit of the memory type (AWCACHE[3]) to decide whether to allocate to the L3 cache, as follows:

- If the stash request does not target a core (AWSTASHLPIDENS is LOW) and AWCACHES[3] is HIGH, then the cache line is allocated to the L3 cache.
- When the stash request does not target a core (AWSTASHLPIDENS is LOW), then the WriteUniqueFullStash transaction performs the same operation as WriteUniqueFull.
- If the stash request does not target a core (AWSTASHLPIDENS is LOW) and AWCACHES[3] is LOW, then the cache line is not allocated to the L3 cache. Instead, the cache line is written out on the manager port instead.
- Stash requests that target a core (AWSTASHLPIDENS is HIGH) always attempt to allocate to the core L2 cache. The value of AWCACHES[3] does not affect the allocation.

### Heavy ACP traffic

Some data buffering is shared between the ACP interface and the cores. Therefore, heavy traffic on the ACP interface might reduce the performance of the cores.

### ACP acceptance capabilities

The following table describes the ACP acceptance capabilities.

<table id="nax1660577279327__table_v5q_p2f_vz">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   ACP acceptance capabilities for each ACP port
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d339331e187" rowspan="1">
    Attribute
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d339331e190" rowspan="1">
    Value
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d339331e193" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Write acceptance capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    256
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The ACP can accept up to 256 write transactions depending on configuration. The total is limited to the
    <code class="documents-parmname">
     NUM_LTDBS
    </code>
    parameter multiplied by the
    <code class="documents-parmname">
     NUM_L3_SLICES
    </code>
    parameter.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Read acceptance capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    256
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The ACP can accept up to 256 read transactions depending on configuration. The total is limited to the
    <code class="documents-parmname">
     NUM_LTDBS
    </code>
    parameter multiplied by the
    <code class="documents-parmname">
     NUM_L3_SLICES
    </code>
    parameter.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Combined acceptance capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    512
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The ACP can accept up to 512 transactions depending on configuration. The total across the whole cluster is limited to the
    <code class="documents-parmname">
     NUM_LTDBS
    </code>
    parameter multiplied by the
    <code class="documents-parmname">
     NUM_L3_SLICES
    </code>
    parameter.
   </td>
  </tr>
 </tbody>
</table>

### Related information

- [ACP features](/documentation/107721/0001/ACP-subordinate-interface/ACP-features?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification and includes support for atomic transactions and cache stashing. Memory tagging is also supported but only to a basic level as defined by the AMBA specification. This allows reading and writing the tags but does not support tag matching on writes.")
- [ACP ACE5-LiteDVM protocol subset](/documentation/107721/0001/ACP-subordinate-interface/ACP-ACE5-LiteDVM-protocol-subset?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification that includes support for Cacheable, Non-cacheable, and Device memory accesses.")
- [ACP transactions](/documentation/107721/0001/ACP-subordinate-interface/ACP-transactions?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification. The ACP interface includes support for Cacheable, Non-cacheable, Device, and Atomic memory accesses.")
