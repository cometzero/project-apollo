# PMU events

Source: <https://developer.arm.com/documentation/107721/0001/Performance-Monitors-Extension-support-/PMU-events>

### PMU events

The following table shows the events that are generated and the numbers that the Performance Monitoring Unit (PMU) uses to reference the events.

<table id="onx1660577315324__table_xkm_rpy_wz">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PMU events
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d55528e66" rowspan="1">
    PMU event number
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55528e69" rowspan="1">
    Event mnemonic
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d55528e72" rowspan="1">
    Event description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0011
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CYCLES
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cycle counter
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0019
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    BUS_ACCESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus access counter
    </p>
    <p>
     Counts every beat of data that is transferred over the data channels between the Snoop Control Unit (SCU) and the interconnect. If both read and write beats are transferred on a given cycle, this event is counted twice on that cycle.
    </p>
    <p>
     This event counts the sum of BUS_ACCESS_RD and BUS_ACCESS_WR.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x001A
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MEMORY_ERROR
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Local memory error counter
    </p>
    <p>
     Counts for each cycle where there is a Correctable or Uncorrectable memory error (Error Correcting Code (ECC) or parity) in the protected RAMs.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x001D
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    BUS_CYCLES
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    ACE or CHI bus cycle counter.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0029
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3D_CACHE_ALLOCATE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 unified cache allocation without refill counter.
    </p>
    <p>
     Counts every full cache line write into the L3 cache which does not cause a linefill.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x002A
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3D_CACHE_REFILL
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 unified cache refill counter
    </p>
    <p>
     Counts every Cacheable read transaction issued to the interconnect.
    </p>
    <p>
     This event counts the sum of L3D_CACHE_REFILL_RD and L3D_CACHE_REFILL_WR.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x002B
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3D_CACHE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 unified cache access counter
    </p>
    <p>
     Counts every Cacheable read or write transaction issued to the Snoop Control Unit (SCU).
    </p>
    <p>
     This event counts the sum of L3D_CACHE_RD and L3D_CACHE_WR.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x002C
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3D_CACHE_WB
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 unified cache write-back counter
    </p>
    <p>
     Counts every write-back from the L3 cache.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0060
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    BUS_ACCESS_RD
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus access, read counter
    </p>
    <p>
     Counts every beat of data transferred over the read data channel between the SCU and the interconnect.
    </p>
    <blockquote id="onx1660577315324__note_w5122ab1b9b1b1b3b9c17b5b5_w5123ab1b9b1b1b3b9c17b5_w5124ab1b9b1b1b3b9c17_w5125ab1b9b1b1b3b9_w5126ab1b9b1b1b3_w5127ab1b9b1b1_w5128ab1b9b1_w5129ab1b9_w5130ab1" title="Note info">
     <h3 class="documents-underline">
      Note
     </h3>
     If the cluster generates a CHI MakeReadUnique transaction for a shared line upgrade, it is unknown at the time of counting if this results in a data transfer or not. Therefore, the counter assumes the data will not be transferred.
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0061
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    BUS_ACCESS_WR
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus access, write counter
    </p>
    <p>
     Counts every beat of data transferred over the write data channel between the SCU and the interconnect.
    </p>
    <blockquote id="onx1660577315324__note_w5131ab1b9b1b1b3b9c19b5b5_w5132ab1b9b1b1b3b9c19b5_w5133ab1b9b1b1b3b9c19_w5134ab1b9b1b1b3b9_w5135ab1b9b1b1b3_w5136ab1b9b1b1_w5137ab1b9b1_w5138ab1b9_w5139ab1" title="Note info">
     <h3 class="documents-underline">
      Note
     </h3>
     If the cluster generates a CHI WriteEvictOrEvict transaction for a clean eviction, it is unknown at the time of counting if this results in a data transfer or not. Therefore, the counter assumes the data will be transferred.
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0062
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    BUS_ACCESS_SHARED
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus access, shared counter
    </p>
    <p>
     Counts every beat of shared data transferred over the data channels between the SCU and the interconnect.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0063
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    BUS_ACCESS_NOT_SHARED
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus access, not shared counter
    </p>
    <p>
     Counts every beat of not shared data transferred over the write data channel between the SCU and the interconnect.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0064
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    BUS_ACCESS_NORMAL
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus access, normal counter
    </p>
    <p>
     Counts every beat of normal data transferred over the write data channel between the SCU and the interconnect.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0065
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    BUS_ACCESS_PERIPH
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus access, periph counter
    </p>
    <p>
     Counts every beat of Device data transferred over the write data channel between the SCU and the interconnect.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00A0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3D_CACHE_RD
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 unified cache access, read counter
    </p>
    <p>
     Counts every Cacheable shareable read transaction that is issued to the SCU. Prefetches and stashes are not counted.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00A1
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3D_CACHE_WR
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 unified cache access, write counter
    </p>
    <p>
     Counts every Cacheable write transaction issued to the SCU.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00A2
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3D_CACHE_REFILL_RD
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 unified cache refill, read counter
    </p>
    <p>
     Counts every Cacheable read transaction issued to the interconnect caused by a Cacheable shareable read transaction. Prefetches and stashes are not counted.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00A3
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3D_CACHE_REFILL_WR
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     L3 unified cache refill, write counter
    </p>
    <p>
     Counts every Cacheable read transaction issued to the interconnect caused by a write transaction.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0119
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACP_ACCESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Accelerator Coherency Port (ACP) access counter
    </p>
    <p>
     Counts every beat of data transferred over the data channels between the SCU and the ACP. If both read and write data beats are transferred on a given cycle, this event is counted twice on that cycle.
    </p>
    <p>
     This event counts the sum of ACP_ACCESS_RD and ACP_ACCESS_WR.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x011D
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACP_CYCLES
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    ACP cycle counter
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0160
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACP_ACCESS_RD
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     ACP access, read counter
    </p>
    <p>
     Counts every beat of data transferred over the read data channel between the SCU and the peripheral port.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0161
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACP_ACCESS_WR
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     ACP access, write counter
    </p>
    <p>
     Counts every beat of data transferred over the write data channel between the SCU and the peripheral port.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0219
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PPT_ACCESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral port access counter
    </p>
    <p>
     Counts every beat of data transferred over the data channels between the SCU and the peripheral port. If both read and write data beats are transferred on a given cycle, this event is counted twice on that cycle.
    </p>
    <p>
     This event counts the sum of PP_ACCESS_RD and PP_ACCESS_WR.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x021D
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PP_CYCLES
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral port cycle counter
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0260
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PP_ACCESS_RD
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral port access, read counter.
    </p>
    <p>
     Counts every beat of data transferred over the read data channel between the SCU and the peripheral port.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0261
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PP_ACCESS_WR
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral port access, write counter
    </p>
    <p>
     Counts every beat of data transferred over the write data channel between the SCU and the peripheral port.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00C0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_SNP_ACCESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Snoop access counter
    </p>
    <p>
     Counts every snoop request
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00C1
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_SNP_EVICT
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     SNP evictions counter
    </p>
    <p>
     Counts every invalidating external snoop request that causes an L3 cache eviction.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00C2
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_SNP_NO_CPU_SNP
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     SNP, no CPU snoop counter
    </p>
    <p>
     Counts every external snoop request that completes without needing to snoop a core.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0500
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_PFTCH_CPU_ACCESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Prefetch access, CPU counter
    </p>
    <p>
     Counts every stash transaction originating from a core.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0501
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_PFTCH_CPU_MISS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Prefetch data miss, CPU counter
    </p>
    <p>
     Counts every stash transaction originating from a core where data was read in from outside the cluster.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0502
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_PFTCH_CPU_HIT
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Prefetch data hit, CPU counter
    </p>
    <p>
     Counts every stash transaction originating from a
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     where either:
    </p>
    <ul id="onx1660577315324__ul_kt2_4k1_ksb">
     <li>
      The stash hit in the cluster or;
     </li>
     <li>
      The stash is not performed due to the L3 cache being off.
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0510
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_STASH_ICN_ACCESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Stash access, ICN counter
    </p>
    <p>
     Counts every stash transaction originating from the interconnect.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0511
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_STASH_ICN_MISS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Stash data miss, ICN counter
    </p>
    <p>
     Counts every stash transaction originating from the interconnect which utilizes a data pull, or is added to the stash queue and later issues a read.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0512
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_STASH_ICN_HIT
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Stash data hit, ICN counter
    </p>
    <p>
     Counts every non-invalidating stash transaction originating from the interconnect which hits in the cluster
    </p>
    .
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0515
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_STASH_ICN_DROPPED
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Stash dropped, ICN counter
    </p>
    <p>
     Counter for every dropped stash transaction originating from the interconnect for which a data-pull of read are not used due to a lack of resources or the L3 cache being off.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0520
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_STASH_ACP_ACCESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Stash access, ACP counter
    <p>
     Counter for every stash-supported transaction originating from an ACP.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0521
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_STASH_ACP_MISS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Stash data miss, ACP counter. Counter for every dataless stash transaction originating from ACP where data was read in from outside the cluster.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0522
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_STASH_ACP_HIT
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Stash data hit, ACP counter
    </p>
    <p>
     Counter for every dataless stash transaction originating from the ACP where either:
    </p>
    <ul id="onx1660577315324__ul_k5r_2l1_ksb">
     <li>
      The stash hit in the cluster or;
     </li>
     <li>
      The stash was not performed due to L3 cache being off.
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00D0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_HZD_ADDRESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Arbitration hazard, address counter
    </p>
    <p>
     Counts every flush caused by an address hazard.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00F3
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_BIB_ACCESS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Counts every snoop filter access due to snoop filter maintenance activity.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00F4
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SCU_BACK_INVALIDATE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Back invalidation counter
    </p>
    <p>
     Counts when a
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     must be snooped to invalidate a line because of not enough capacity in the snoop filter.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00F5
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SCU_BIB_ECC
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     BIB ECC errors counter
    </p>
    <p>
     ECC errors detected on a back invalidation accesses that cause a way to be avoided but are not corrected or reported in the Reliability, Availability, and Serviceability (RAS) registers.
    </p>
   </td>
  </tr>
 </tbody>
</table>
