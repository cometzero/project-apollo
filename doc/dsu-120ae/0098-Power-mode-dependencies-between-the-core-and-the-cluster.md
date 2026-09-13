# Power mode dependencies between the core and the cluster

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Power-mode-dependencies-between-the-core-and-the-cluster>

### Power mode dependencies between the core and the cluster

There are some dependencies between the Power Policy Unit (PPU) modes of core and the PPU modes of DSU-120AE DynamIQ™ cluster to ensure that the correct operation is maintained.

The following table describes dependencies on the requested core PPU modes.

<table id="ddr1660577254528__table_vmq_dyt_3jb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU mode dependencies for
   <span>
    <span class="documents-keyword">
     core
    </span>
   </span>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d189814e91" rowspan="1">
    Current
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    PPU mode
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d189814e98" rowspan="1">
    Requested
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    PPU mode
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d189814e105" rowspan="1">
    Cluster dependency
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d189814e108" rowspan="1">
    Effect on
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OFF or OFF_EMU
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    The
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    can only transition to ON once the cluster is in ON, cluster FULL_RET or FUNC_RET.
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    request stalls until the cluster has reached the appropriate state.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WARM_RST
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    The cluster must have previously transitioned from ON to WARM_RST, and then from WARM_RST back to ON, before the
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    request can be accepted.
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    request stalls until the cluster has transitioned from WARM_RST to ON.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    DBG_RECOV
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    The cluster must have previously transitioned from ON to DBG_RECOV, and then from DBG_RECOV back to ON, before the
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    request can be accepted.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    request stalls until the cluster has transitioned from DBG_RECOV to ON.
   </td>
  </tr>
 </tbody>
</table>

The following table describes dependencies on the requested DSU-120AE DynamIQ™ cluster PPU modes.

<table id="ddr1660577254528__table_opc_ryt_3jb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   PPU mode dependencies for cluster
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
   <th class="documents-nocellnorowborder" colspan="1" id="d189814e220" rowspan="1">
    Current cluster PPU mode
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d189814e223" rowspan="1">
    Requested cluster PPU mode
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d189814e226" rowspan="1">
    Dependency
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d189814e229" rowspan="1">
    Effect on cluster
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MEM_RET or OFF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Not all
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    are OFF
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster PPU mode request is denied
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OFF/OFF_EMU/MEM_RET/MEM_RET_EMU
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    If the Accelerator Coherency Port (ACP) interface is present and
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      SYSCOREQS
     </span>
    </span>
    is asserted
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster PPU mode request is denied
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MEM_RET_EMU or OFF_EMU
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Not all
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    in OFF or OFF_EMU
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster PPU mode request is denied
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    If a
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    has requested to leave OFF mode whilst an L3 cache data clean and invalidate is in progress
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    L3 cache clean and invalidate process is abandoned and cluster PPU mode OFF request is denied
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WARM_RST
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Cores
    </span>
    not in OFF, OFF_EMU, WARM_RST, or DBG_RECOV
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster PPU mode request is denied
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    DBG_RECOV
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span>
     Cores
    </span>
    not in OFF, OFF_EMU, WARM_RST, or DBG_RECOV
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cluster PPU mode request is denied
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> For information on power mode dependencies between
> cores in a dual-
> core
> complex, see
> [Power mode transition dependencies for a dual-core complex](/documentation/107721/0001/Power-management/Complex-power-management/Power-mode-transition-dependencies-for-a-dual-core--complex?lang=en "When there are two cores in the same complex, the power modes of the two cores must be consistent with the power mode of the shared logic. The Power Policy Units (PPUs) have logic to ensure that these requirements are maintained automatically.").
