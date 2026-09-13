# Power states for the cluster RAM instances

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Power-states-for-the-cluster-RAM-instances>

### Power states for the cluster RAM instances

The cluster power mode controls the power states requested for the L3 data and L3 tag RAM instances.

This table shows which combinations of slices are powered on and active in four different slice configurations.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   <span class="documents-keyword">
    DSU-120AE
   </span>
   Slice activity for 1, 2, 4, and 8 slice configurations
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
   <th class="documents-cellrowborder" colspan="1" id="d221076e81" rowspan="2">
    &nbsp;
   </th>
   <th class="documents-cellrowborder" colspan="2" id="d221076e83" rowspan="1">
    1 slice configuration
   </th>
   <th class="documents-cellrowborder" colspan="2" id="d221076e86" rowspan="1">
    2 slice configuration
   </th>
   <th class="documents-cellrowborder" colspan="2" id="d221076e89" rowspan="1">
    4 slice configuration
   </th>
   <th class="documents-cellrowborder" colspan="2" id="d221076e92" rowspan="1">
    8 slice configuration
   </th>
  </tr>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d221076e98" rowspan="1">
    Active
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e101" rowspan="1">
    Inactive
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e104" rowspan="1">
    Active
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e107" rowspan="1">
    Inactive
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e110" rowspan="1">
    Active
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e114" rowspan="1">
    Inactive
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e117" rowspan="1">
    Active
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e120" rowspan="1">
    Inactive
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    One Slice
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1, 2, 3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1, 2, 3, 4, 5, 6, 7
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Half Slices
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0, 1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2, 3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0, 1, 2, 3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4, 5, 6, 7
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All Slices
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0, 1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0, 1, 2, 3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0, 1, 2, 3, 4, 5, 6, 7
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

The following two tables show the power state dependencies between the cluster Power Policy Unit (PPU) and those signaled on the Power Control State Machine (PCSM) output. They also show the internal power states for the L3 data cache and L3 tag RAM instances, and the cluster and slice power domains.

> ### Note
>
> In the following two tables:
>
> - N is the number of L3 cache slices.
> - The internal power modes, for example, off and retention, are written in lowercase lettering as compared to cluster power modes which are written in uppercase lettering.
> - The cluster power mode ON state includes the WARM\_RST, DBG\_RECOV, and MEM\_RET\_EMU states.
> - The term retention is abbreviated ( ret.).

The following table shows the power state dependencies for:

- L3 cache slice 0
- L3 cache slices 1 to N, when the ALL SLICE operating mode is selected.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   <span class="documents-keyword">
    DSU-120AE
   </span>
   RAM power states for an active cache slice
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
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d221076e309" rowspan="1">
    Cluster power mode
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d221076e312" rowspan="1">
    ON, OFF_EMU
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d221076e315" rowspan="1">
    FUNC_RET
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d221076e318" rowspan="1">
    FULL_RET
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d221076e321" rowspan="1">
    MEM_RET
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e325" rowspan="1">
    OFF
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    CLUSTER PCSM PSTATE power mode
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    MEM_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OFF
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Operating mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SF ONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SF ONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SF ONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SF ONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    N/A
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Power portion
    </span>
    1 L3 data and tag RAMs
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Power portion
    </span>
    0 L3 data and tag RAMs. Also victim RAMs
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Snoop Filter SF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ret.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    LTDB RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Associated PDSLICE power domain state
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    PDCLUSTER power domain logic
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    on
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> The power portions 0 and 1 each consist of eight cache ways with one cache way for each of the eight Memory system resource Partitioning And Monitoring (MPAM) cache partitions. Therefore, powering down power-portion 1 powers down one cache way in each MPAM partition. For more information, see
> [L3 cache partitioning](/documentation/107721/0001/L3-cache/L3-cache-partitioning?lang=en "The L3 cache supports a partitioning scheme that alters the cache allocation and victim selection policy to prevent processes from using the entire L3 cache to the disadvantage of other processes.").

The following table shows the power state dependencies for an inactive cache slice:

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   <span class="documents-keyword">
    DSU-120AE
   </span>
   RAM power states for an inactive cache slice
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
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d221076e751" rowspan="1">
    Cluster power mode
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d221076e754" rowspan="1">
    ON, OFF_EMU
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d221076e757" rowspan="1">
    FUNC_RET
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d221076e760" rowspan="1">
    FULL_RET
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d221076e763" rowspan="1">
    MEM_RET
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d221076e767" rowspan="1">
    OFF
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    CLUSTER PCSM PSTATE power mode
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-cellrowborder" colspan="3" rowspan="1">
    MEM_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OFF
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Operating mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SF ONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SF ONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SF ONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SF ONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    N/A
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Power portion
    </span>
    1 L3 data and tag RAMs
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Power portion
    </span>
    0 L3 data and tag RAMs. Also victim RAMs
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Snoop Filter SF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    LTDB RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Associated PDSLICE power domain state
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    PDCLUSTER power domain logic
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    off
   </td>
  </tr>
 </tbody>
</table>
