# CHI peripheral port transactions

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/CHI-peripheral-port-transactions>

### CHI peripheral port transactions

The CHI configured peripheral port of DynamIQ™ Shared Unit-120AE (DSU-120AE) supports the same CHI transactions as the CHI configured main requester interface.

The following table shows the read and write transactions supported by the CHI-configured peripheral port of the DSU-120AE.

<table class="documents-tableborder">
 <tbody>
  <tr>
   <td colspan="1" rowspan="1">
    <table>
     <caption>
      <span class="documents-tablecap">
       <span class="documents-table--title-label">
        Table 1.
       </span>
       CHI read and write transactions supported by
       <span class="documents-keyword">
        DSU-120AE
       </span>
      </span>
     </caption>
     <colgroup>
      <col span="1"/>
      <col span="1"/>
      <col span="1"/>
     </colgroup>
     <thead>
      <tr>
       <th class="documents-row-nocellborder" colspan="1" id="d191524e83" rowspan="1">
        Transaction
       </th>
       <th class="documents-row-nocellborder" colspan="1" id="d191524e86" rowspan="1">
        Operation
       </th>
       <th class="documents-cellrowborder" colspan="1" id="d191524e89" rowspan="1">
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
        Cache maintenance instructions. The Data Cache Clean to the Point of Persistence (DC CVAP) cache maintenance instruction generates this transaction when the
        <span class="documents-g.signal.name">
         <span class="documents-keyword">
          BROADCASTPERSISTMP
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
       <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
        DVMOp
       </td>
       <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
        Translation Lookaside Buffer (TLB) and instruction cache maintenance instructions when enabled by the
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
        input signals.
       </td>
       <td class="documents-cell-norowborder" colspan="1" rowspan="1">
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
        Store instructions of a full cache line of data that miss in the caches
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
        Reading Memory Tagging Extension (MTE) tags for a Cacheable shareable line that is already cached in the cluster without tags
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
        Non-cacheable loads or instruction fetches, or cache linefills of Non-shareable cache lines into L1 or L2 caches
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
        Speculative store to Cacheable shareable memory or, if Excl is HIGH, a load exclusive instruction
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
        Cache prefetch when the L3 cache is not present or powered down and configured by the CLUSTERECTLR_EL1
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
       </td>
      </tr>
      <tr>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        StashOnceSepUnique
       </td>
       <td class="documents-row-nocellborder" colspan="1" rowspan="1">
        Cache prefetch when the L3 cache is not present or powered down and configured by the CLUSTERECTLR_EL1
       </td>
       <td class="documents-cellrowborder" colspan="1" rowspan="1">
        No
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
        Evictions of dirty lines from the L3 cache, when the line is still present in an L1 or L2 cache
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
        Evictions of clean lines, when configured in the CLUSTERECTLR_EL1
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
        Non-cacheable store instructions. Evictions of Non-shareable cache lines.
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
        Write of zeroes to Non-cacheable or Non-shareable memory using the DC ZVA instruction
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
        Write of zeroes to a Shareable cache line using the DC ZVA instruction
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
