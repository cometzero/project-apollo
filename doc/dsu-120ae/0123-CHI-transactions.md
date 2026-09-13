# CHI transactions

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/CHI-transactions>

### CHI transactions

CHI transactions are sent to a specific node in the interconnect depending on type of access, the address of the access, and settings in the system address map.

Addresses that map to an HN-F node can be marked as Cacheable memory in the translation tables, and can take part in the cache coherency protocol. Addresses that map to an HN-I or MN must be marked as device or Non-cacheable memory.

CHI TXREQ transactions include the Logical processor ID (LPID) field. This field uniquely identifies the logical core that generated the request transaction. The following table shows CHI LPID[4:0] bitfields:

> ### Note
>
> For a Translation Lookaside Buffer (TLB) translation table walk from a complex, the LPID information is only accurate to the granularity of the complex. Therefore, the LPID might indicate any Processing Element (PE) within the complex. You can determine a TLB translation table walk by the signal TXREQSRCATTRMx[1:0]=0b10.

<table id="gvh1660577267936__table_lpid">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CHI LPID[4:0] bitfields
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
   <th class="documents-cellrowborder" colspan="1" id="d85695e105" rowspan="1">
    LPID[4:0] bit field
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d85695e108" rowspan="1">
    Accelerator Coherency Port (ACP) not implemented
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d85695e113" rowspan="1">
    One ACP port implemented
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d85695e116" rowspan="1">
    Two ACP ports implemented
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      0
     </dt>
     <dd>
      If
      <span class="documents-g.signal.name">
       <span class="documents-keyword">
        LPID[3:0]
       </span>
      </span>
      is
      <span class="documents-g.number.hex">
       0xE
      </span>
     </dd>
     <dt class="documents-dlterm">
      Reserved
     </dt>
     <dd>
      If
      <span class="documents-g.signal.name">
       <span class="documents-keyword">
        LPID[3:0]
       </span>
      </span>
      is not
      <span class="documents-g.number.hex">
       0xE
      </span>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      0
     </dt>
     <dd>
      If
      <span class="documents-g.signal.name">
       <span class="documents-keyword">
        LPID[3:0]
       </span>
      </span>
      is
      <span class="documents-g.number.hex">
       0xE
      </span>
      and ACP interface 0
     </dd>
     <dt class="documents-dlterm">
      1
     </dt>
     <dd>
      If
      <span class="documents-g.signal.name">
       <span class="documents-keyword">
        LPID[3:0]
       </span>
      </span>
      is
      <span class="documents-g.number.hex">
       0xE
      </span>
      and ACP interface 1
     </dd>
     <dt class="documents-dlterm">
      Reserved
     </dt>
     <dd>
      If
      <span class="documents-g.signal.name">
       <span class="documents-keyword">
        LPID[3:0]
       </span>
      </span>
      is not
      <span class="documents-g.number.hex">
       0xE
      </span>
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0x0
      </span>
      -
      <span class="documents-g.number.hex">
       0xD
      </span>
     </dt>
     <dd>
      Core instance number
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0xF
      </span>
     </dt>
     <dd>
      Cache copyback
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0xE
      </span>
     </dt>
     <dd>
      Accelerator Coherency Port (ACP) interface 0
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0xE
      </span>
     </dt>
     <dd>
      Accelerator Coherency Port (ACP) interface 1
     </dd>
    </dl>
   </td>
  </tr>
 </tbody>
</table>

The following table shows the CHI read and write transaction types supported by the CHI-configured requester port on the DynamIQ Shared Unit-120AE (DSU-120AE).

<table class="documents-tableborder">
 <tbody>
  <tr>
   <td colspan="1" rowspan="1">
    <table id="gvh1660577267936__chi_transactions">
     <caption>
      <span class="documents-tablecap">
       <span class="documents-table--title-label">
        Table 2.
       </span>
       CHI read and write transactions supported by CHI-configured
       <span class="documents-keyword">
        requester
       </span>
       port
      </span>
     </caption>
     <colgroup>
      <col span="1"/>
      <col span="1"/>
      <col span="1"/>
     </colgroup>
     <thead>
      <tr>
       <th class="documents-row-nocellborder" colspan="1" id="d85695e322" rowspan="1">
        Transaction
       </th>
       <th class="documents-row-nocellborder" colspan="1" id="d85695e325" rowspan="1">
        Operation
       </th>
       <th class="documents-cellrowborder" colspan="1" id="d85695e328" rowspan="1">
        Produced by
        <span class="documents-keyword">
         DSU-120AE
        </span>
       </th>
      </tr>
     </thead>
     <tbody>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        AtomicCompare
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Atomic instruction that is not allocating inside the cluster
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        AtomicLoad
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Atomic instruction that is not allocating inside the cluster
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        AtomicStore
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Atomic instruction that is not allocating inside the cluster
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        AtomicSwap
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Atomic instruction that is not allocating inside the cluster
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        CleanInvalid
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache maintenance instructions
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        CleanShared
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache maintenance instructions
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        CleanSharedPersist
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used. CleanSharedPersistSep is used instead.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        CleanSharedPersistSep
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache maintenance instructions. The Data Cache Clean to the Point of Persistence (
        <code>
         DC CVAP
        </code>
        ) cache maintenance instruction generates this transaction when the
        <span class="documents-g.signal.name">
         <span class="documents-keyword">
          BROADCASTPERSIST
         </span>
        </span>
        input signal is HIGH.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        CleanUnique
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        DVMOp
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Branch predictor maintenance instructions, and Translation Lookaside Buffer (TLB) and instruction cache maintenance instructions when enabled by the
        <span class="documents-g.signal.name">
         <span class="documents-keyword">
          BROADCASTTLBIINNER
         </span>
        </span>
        ,
        <span class="documents-g.signal.name">
         <span class="documents-keyword">
          BROADCASTTLBIOUTER
         </span>
        </span>
        , and
        <span class="documents-g.signal.name">
         <span class="documents-keyword">
          BROADCASTICINVAL
         </span>
        </span>
        input signals
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Evict
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Evictions of clean lines, when configured in the CLUSTERECTLR_EL1
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        MakeInvalid
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        MakeReadUnique
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Store instructions when the line is already cached in a Shared state inside the cluster. This includes store exclusive instructions, which set Excl HIGH.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        MakeUnique
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Store instructions of a full cache line of data that miss in the caches.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        PCrdReturn
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        PrefetchTgt
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Hardware prefetch hint to the memory controller
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadClean
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Reading Memory Tagging Extension (MTE) tags for a Cacheable shareable line that is already cached in the cluster without tags.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadNoSnp
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Non-cacheable loads or instruction fetches, or cache linefills of Non-shareable cache lines into L1 or L2 caches.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadNoSnpSep
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadNotSharedDirty
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache data linefills started by a load instruction, or cache linefills started by an instruction fetch
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadOnce
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cacheable shareable instruction fetches that are not allocating into a coherent cache
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadOnceCleanInvalid
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadOnceMakeInvalid
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadPreferUnique
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Speculative store to Cacheable shareable memory or, if Excl is HIGH, a load exclusive instruction.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadShared
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReadUnique
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache data linefills started by a store instruction
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        ReqLCrdReturn
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Link credit return
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        StashOnceSepShared
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache prefetch when the L3 cache is not present or powered down. Configured by CLUSTERECTLR_EL1.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Not generated
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        StashOnceSepUnique
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache prefetch when the L3 cache is not present or powered down. Configured by CLUSTERECTLR_EL1.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Not generated
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        StashOnceShared
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        StashOnceUnique
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteBackFull
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Evictions of dirty cacheable shareable lines from the cluster
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteBackFullCMO
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache maintenance instruction evicting a dirty shareable cache line
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteBackPtl
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteCleanFull
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Evictions of dirty lines from the L3 cache, when the line is still present in an L1 or L2 cache.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteCleanFullCMO
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache maintenance instruction cleaning a dirty shareable cache line
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteEvictFull
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Evictions of clean lines, when configured in the CLUSTERECTLR_EL1
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteEvictOrEvict
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Evictions of clean lines, when configured in the CLUSTERECTLR_EL1 register.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteNoSnpFull
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Non-cacheable store instructions. Evictions of Non-shareable cache lines
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteNoSnpFullCMO
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache maintenance instruction evicting a dirty Non-shareable cache line
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteNoSnpPtl
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Non-cacheable store instructions
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteNoSnpPtlCMO
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteNoSnpZero
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Write of zeroes to Non-cacheable or Non-shareable memory using the
        <code>
         DC ZVA
        </code>
        instruction.
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteUniqueFull
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cacheable writes of a full cache line not allocating into L1, L2, or L3 caches, for example streaming writes
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteUniqueFullCMO
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteUniqueFullStash
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteUniquePtl
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Generated as a result of Accelerator Coherency Port (ACP) WriteUniquePtl transactions when not allocating to the L3 cache
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteUniquePtlCMO
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteUniquePtlStash
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Not used
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        WriteUniqueZero
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Write of zeroes to a Shareable cache line using the
        <code>
         DC ZVA
        </code>
        instruction
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        Yes
       </td>
      </tr>
     </tbody>
    </table>
   </td>
  </tr>
 </tbody>
</table>

The following table shows the transactions generated by external memory accesses in an implementation configured with a CHI requester interface.

<table id="gvh1660577267936__table_w8814ab1c11b3c11_w8815ab1c11b3_w8816ab1c11_w8817ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   CHI transaction usage
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
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="2" id="d85695e1013" rowspan="1">
    Attributes
   </th>
   <th class="documents-cell-norowborder" colspan="5" id="d85695e1016" rowspan="1">
    CHI transaction
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d85695e1022" rowspan="1">
    Memory type
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d85695e1025" rowspan="1">
    Shareability
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d85695e1028" rowspan="1">
    SnpAttr
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d85695e1031" rowspan="1">
    Load
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d85695e1034" rowspan="1">
    Store
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d85695e1038" rowspan="1">
    Load exclusive
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d85695e1041" rowspan="1">
    Store exclusive
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Device
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Outer Shareable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Non-snoopable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ReadNoSnp
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WriteNoSnp
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ReadNoSnp and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       Excl
      </span>
     </span>
     set to HIGH.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     WriteNoSnp and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       Excl
      </span>
     </span>
     set to HIGH.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    <p>
     Normal, Inner Non-cacheable, Outer Non-cacheable
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Non-shareable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    Non-snoopable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    ReadNoSnp
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    WriteNoSnp
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    <p>
     ReadNoSnp and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       Excl
      </span>
     </span>
     set to HIGH.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="3">
    WriteNoSnp and
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      Excl
     </span>
    </span>
    set to HIGH.
   </td>
  </tr>
  <tr>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Inner Shareable
   </td>
  </tr>
  <tr>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Outer Shareable
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    <p>
     Normal, Inner Non-cacheable, Outer Write-Back or Write-Through, or Normal, Inner Write-Through, Outer Write-Back, Write-Through or Non-cacheable, or Normal Inner Write-Back Outer Non-cacheable or Write-Through
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Non-shareable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    Non-snoopable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    ReadNoSnp
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    WriteNoSnp
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    ReadNoSnp and
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      Excl
     </span>
    </span>
    set to HIGH.
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="3">
    <p>
     WriteNoSnp and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       Excl
      </span>
     </span>
     set to HIGH.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Inner Shareable
   </td>
  </tr>
  <tr>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Outer Shareable
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    Normal, Inner Write-Back, Outer Write-Back
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Non-shareable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Non-snoopable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ReadNoSnp
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WriteNoSnp when the line is evicted or if not allocating into the cache.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ReadNoSnp
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     WriteNoSnp when the line is evicted.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Inner Shareable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Snoopable
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="2">
    ReadNotSharedDirty or ReadClean
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="2">
    <p>
     ReadUnique, MakeReadUnique, or MakeUnique if allocating into the cache, then a WriteBackFull when the line is evicted.
    </p>
    <p>
     WriteUniqueFull if not allocating into the cache.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="2">
    ReadNotSharedDirty, ReadClean, or ReadPreferUnique with
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      Excl
     </span>
    </span>
    set to HIGH.
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="2">
    MakeReadUnique with
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      Excl
     </span>
    </span>
    set to HIGH if required, then a WriteBackFull when the line is evicted.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Outer Shareable
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Snoopable
   </td>
  </tr>
 </tbody>
</table>

The DSU-120AE never sends SnpRespDataPtl, NCBWrDataCompAck, or WriteDataCancel packets.
