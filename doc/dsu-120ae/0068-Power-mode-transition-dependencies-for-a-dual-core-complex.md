# Power mode transition dependencies for a dual-core complex

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Complex-power-management/Power-mode-transition-dependencies-for-a-dual-core--complex>

### Power mode transition dependencies for a dual-core complex

When there are two cores in the same complex, the power modes of the two cores must be consistent with the power mode of the shared logic. The Power Policy Units (PPUs) have logic to ensure that these requirements are maintained automatically.

In some cases when both cores request a power transition at the same time, the PPU logic delays the transition of the second core until the first core has completed its transition.

There are some cases where a power transition on one core might require a power transition on the other core to take place before the first core can progress.

The following table describes the power mode transitioning dependencies between the cores in a dual-core complex.

<table id="cks1660577242136__table_k5p_txc_nsb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Complex core power mode dependencies
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d266451e131" rowspan="1">
    <span>
     Core
    </span>
    A power mode
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d266451e136" rowspan="1">
    <span>
     Core
    </span>
    B power mode
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d266451e141" rowspan="1">
    <span>
     Core
    </span>
    A dependency
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d266451e146" rowspan="1">
    Power mode dependency
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d266451e149" rowspan="1">
    PPU request
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL_RET or FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span>
      Core
     </span>
     A carries out one of the following:
    </p>
    <ul id="cks1660577242136__ul_igj_2db_psb">
     <li>
      Makes a request from ON mode to OFF mode.
     </li>
     <li>
      Makes a request from ON mode to OFF_EMU mode.
     </li>
     <li>
      Requests a reset using the RMR.RR register bit field.
     </li>
    </ul>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    B must be in the ON power mode before
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    A can transition.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span>
     Core
    </span>
    B automatically indicates that it must transition from FULL_RET or FUNC_RET mode to ON mode. The
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    PPU must request this transition for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    B before
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    A transition can proceed.
   </td>
  </tr>
 </tbody>
</table>

The DEVPACTIVE\* inputs to the PPUs indicate that the core B must transition to ON mode, and so if the PPUs are in dynamic mode then this is handled automatically. If the PPUs are in static mode then the component programming the PPUs must ensure that this transition can happen. However, Arm recommends that FUNC\_RET and FULL\_RET modes are not used when the PPUs are in static mode, see [Core Full retention mode and static mode restrictions](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Core-Full-retention-mode-and-static-mode-restrictions?lang=en "The use of Full retention (FULL_RET) mode for a core is not recommended when the Power Policy Unit (PPU) is programmed in static mode.").
