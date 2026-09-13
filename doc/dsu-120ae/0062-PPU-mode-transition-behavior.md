# PPU mode transition behavior

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-PPU-mode-transitions/PPU-mode-transition-behavior>

### PPU mode transition behavior

Where there is a transition between PPU modes, the DSU-120AE cluster logic automatically performs a series of actions before accepting a new PPU mode.

The following table shows the allowed transitions between the cluster PPU modes and the associated actions.

> ### Note
>
> For each of the
> PPU mode transitions shown in the following table, additional actions (which are technology and implementation dependent) must be performed. These actions are carried out by partner implemented logic as part of the Power Control State Machine (PCSM). For more information about the PCSM, see
> [Power policy unit operation](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Power-policy-unit-operation?lang=en "The Power Policy Unit (PPU) supports all the DSU-120AE DynamIQ cluster power modes (ON, OFF, FUNC_RET, FULL_RET, MEM_RET, OFF_EMU, MEM_RET_EMU, WARM_RST, DBG_RECOV), and operating modes. It has extensive support to reflect the various combinations of logic and memory power states into which a domain can be set.").

<table id="szh1660577238540__table_cluster_domain_behavior">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Cluster domain
   <span>
    <span class="documents-keyword">
     PPU mode
    </span>
   </span>
   transition behavior
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d23497e110" rowspan="1">
    Start
    <span>
     <span class="documents-keyword">
      PPU mode
     </span>
    </span>
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d23497e116" rowspan="1">
    End
    <span>
     <span class="documents-keyword">
      PPU mode
     </span>
    </span>
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d23497e122" rowspan="1">
    <span class="documents-keyword">
     DSU-120AE
    </span>
    behavior
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The L3 cache and snoop filter are initialized, and the cluster is brought into coherency with the rest of the system.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    If there is any ongoing
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    or cluster activity, the request is denied. L3 cache allocation disabled, and cleaned and invalidated. The cluster is removed from system coherency.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    If there is any ongoing memory access, the request is denied. Access to the L3 cache RAMs is blocked. Once in FUNC_RET any new transaction to the cache is stalled until there is a return to ON mode.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Access to the L3 cache is allowed.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    If there is any ongoing memory access, the request is denied. Access to the L3 cache RAMs and slice logic is blocked. Once in FULL_RET power mode, any new transaction to the L3 cache is stalled until there is a return to ON mode.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Access to the L3 cache is allowed.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MEM_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    If there is any ongoing
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    or cluster activity, the request is denied.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MEM_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The snoop filter is initialized.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant ways in L3 cache are cleaned and invalidated.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SFONLY ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant ways in L3 cache are cleaned and invalidated.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    SFONLY ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant ways in L3 cache are initialized.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF RAM ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL RAM ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant ways in L3 cache are initialized.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant lines in L3 cache are cleaned and invalidated. Relevant snoop filter entries are emptied, causing back-invalidations to the
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    if necessary.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant lines in L3 cache are cleaned and invalidated. Relevant snoop filter entries are emptied, causing back-invalidations to the
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    if necessary.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant lines in L3 cache are cleaned and invalidated. Relevant snoop filter entries are emptied, causing back-invalidations to the
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    if necessary.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant lines in L3 cache are cleaned and invalidated. Relevant snoop filter entries are emptied, causing back-invalidations to the
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    if necessary.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant lines in L3 cache are cleaned and invalidated. Relevant snoop filter entries are emptied, causing back-invalidations to the
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    if necessary.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Relevant lines in L3 cache are cleaned and invalidated. Relevant snoop filter entries are emptied, causing back-invalidations to the
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    if necessary.
   </td>
  </tr>
 </tbody>
</table>

For information and guidelines on implementing your PCSM, see System Design in Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.
