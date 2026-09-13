# Cache protection behavior

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Cache-protection-behavior>

### Cache protection behavior

The configuration of the Reliability, Availability, Serviceability (RAS) Extension that is implemented in the DynamIQ Shared Unit-120AE (DSU-120AE) includes Error Correcting Code (ECC) cache protection. In this case, the DSU-120AE protects against errors that result in a RAM bitcell holding the incorrect value.

The RAMs in the DSU-120AE support Single Error Correct Double Error Detect (SECDED). SECDED allows detection and correction of any 1-bit error, and detection of any 2-bit error in all protected RAMs. When the datum and code bits are all-zero, or all-one, the interpretation is that an error has occurred that the Error Correcting Code (ECC) scheme cannot correct. However, it might be corrected by other means, such as refetching cached data.

The following table describes the protection type is applied to each RAM. The DSU-120AE can progress and remain functionally correct when there is a single bit error in any RAM.

<table id="lvk1660577290383__table_fgd_s2t_yjb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RAM cache protection
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d14574e98" rowspan="1">
    RAM
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d14574e101" rowspan="1">
    Protection
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d14574e104" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3 data cache data
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ECC, SECDED
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    9 ECC bits per 132 bits
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3 cache tag
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ECC, SECDED
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The number of ECC bits for each 58-bits depend on the size of entry as follows:
    </p>
    <ul id="lvk1660577290383__ul_sbj_nzs_klb">
     <li>
      If the tag entry is 58 bits wide, there are 8 ECC bits.
     </li>
     <li>
      If the tag entry is 57 bits wide or less, there are 7 ECC bits.
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    L3 cache victim
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    None
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Long-Term Data Buffer (LTDB) RAMs
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ECC, SECDED
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    9 ECC bits per 145 bits
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Snoop filter RAMs
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ECC, SECDED
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    7 ECC bits per 48 bits
   </td>
  </tr>
 </tbody>
</table>

### Error correction

If there are multiple single bit errors in different RAMs, or within different protection granules within the same RAM, then the DSU-120AE remains functionally correct.

If there is a double bit error in a single RAM within the same protection granule, the DSU-120AE detects and either reports or defers the error, as consistent with SECDED behavior. If the error is in a cache line containing dirty data, then that data might be lost.

If there are three or more bit errors within the same protection granule, then depending on the RAM and the position of the errors within the RAM, the DSU-120AE might or might not detect the errors. The cache protection feature of the DSU-120AE has a minimal performance impact when no errors are present.

When a correctable error is detected in the L3 cache data RAMs, the data is corrected inline before returning to the requestor.

When a correctable error is detected in the L3 cache tag RAMs or the snoop filter RAMs the following correction mechanism is used:

- The value is corrected and written back to the source address (Read-Correct-Write).
- The lookup is replayed.

The DSU-120AE has extra hardware that provides limited support for hard error correction. A hard error is a physical error in the RAM that prevents the correct value being written. A single hard error can be corrected and is guaranteed to make progress. However, if there are multiple hard errors then, in some cases, this can cause live-locks as the line could continuously replay.

### Uncorrectable errors and Data poisoning

If an error is detected as having 2 bits in error in a RAM protected by ECC, then this error is not correctable. In this case, the behavior depends on the type of RAM, as follows:

Data RAM or Long-Term Data Buffer RAM
:   When an uncorrectable error is detected in an L3 data RAM or Long-Term Data Buffer (LTDB) RAM, the chunk of data with the error is marked as poisoned. This poison status is then transferred with the data and stored:

    - In the cache, if the data is allocated back into a cache.
    - In the LTDB RAM, if the data is moved there.

    The poison status is stored for every 64 bits of data.

    If the interconnect supports poisoning, then the poison status is transferred with the data when the line is evicted or snooped from the cluster. No abort is generated when a line is poisoned. The abort is deferred until a load or instruction fetch consumes the poisoned data.

    If the interconnect does not support poisoning and a poisoned cache line is evicted or snooped from the cluster, then the DSU-120AE generates an interrupt, nCLUSTERERRIRQ, to notify software that data has potentially been lost.

    > ### Note
    >
    > Software can indicate if the interconnect supports poisoning or not by setting the interconnect data poisoning support bit in the Cluster Extended Control Register. See either
    > [IMP\_CLUSTERECTLR\_EL1, Cluster Extended Control Register](/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERECTLR-EL1--Cluster-Extended-Control-Register?lang=en "This register should be used for dynamically changing implementation specific control bits.") or
    > [CLUSTERECTLR, Cluster Extended Control Register](/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-system-control-registers-summary/CLUSTERECTLR--Cluster-Extended-Control-Register?lang=en "This register should be used for dynamically changing implementation specific control bits."), depending on how you are accessing the register.

Tag RAM
:   When an uncorrectable error is detected in an L3 tag RAM, then either the address or coherency state of the line is unknown, so the data cannot be poisoned. In this case, the line is invalidated and the
    DSU-120AE generates an interrupt,
    nCLUSTERERRIRQ, to notify software that data has potentially been lost.

Snoop filter tag RAM
:   When an uncorrectable error is detected in a snoop filter tag RAM, either the address or coherency state of the line is unknown, so the data cannot be poisoned. In this case, the snoop filter entry is invalidated, but the line remains present in one or more of the
    cores. The
    DSU-120AE generates an interrupt,
    nCLUSTERCRITIRQ, to notify software that data has potentially been lost.
    > ### Note
    >
    > Arm recommends that a system reset is performed as soon as possible, in response to this interrupt. This is because the
    > core caches and the snoop filter are inconsistent after this error, which can lead to unpredictable behavior. The effect of the error depends on the type of
    > core, but it could result in further data corruption, or deadlocks, making it impossible to cleanly recover from such an error.

The DSU-120AE does not poison the data transaction of a DVM operation it initiates because the data payload of a DVM operation is not derived from cached data.

If the DSU-120AE receives a poisoned DVM operation from a core, it consumes the error and reports it as an uncorrectable error (`producer error)`. If the DSU must broadcast the poisoned DVM operation, it sets `RespErr=DERR` and `Poison=0` so that the broadcast DVM operation is not marked as poisoned.
