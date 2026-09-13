# Cluster power modes

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes>

### Cluster power modes

The DSU-120AE DynamIQ™ cluster and each of the cores and complexes in the cluster have a defined set of power modes and corresponding legal transitions between these modes.

The following table shows the supported power modes for the DSU-120AE DynamIQ™ cluster.

<table id="etv1660577227267__table_dhk_fnm_p3b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   <span>
    <span class="documents-keyword">
     DSU-120AE DynamIQ&trade; cluster
    </span>
   </span>
   power modes
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d333903e94" rowspan="1">
    Power mode
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d333903e97" rowspan="1">
    Short name
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d333903e100" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    On mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    On mode is the normal mode of operation where all cluster functionality is available.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Off mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    In Off mode, power is removed from the cluster logic and all the RAMs.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Functional retention mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     In Functional retention mode, the L3 cache RAMs and snoop filter RAMs are placed in a retention state. Data is retained in these RAMs.
    </p>
    <p>
     The rest of the
     <span>
      <span class="documents-keyword">
       DynamIQ&trade; cluster shared logic
      </span>
     </span>
     remains powered up.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Full retention mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     In Full retention mode, the L3 cache RAMs and snoop filter RAMs are placed in a retention state, while the cache slice logic is powered down. The rest of the cluster logic such as the bus
     <span class="documents-keyword">
      requesters
     </span>
     , and transport, remains powered.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Memory retention mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MEM_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     In Memory retention mode, only the L3 cache RAMs are placed in retention. The rest of the
     <span>
      <span class="documents-keyword">
       DSU-120AE DynamIQ&trade; cluster
      </span>
     </span>
     including the L3 logic, the
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     , and the
     <span>
      <span class="documents-keyword">
       complexes
      </span>
     </span>
     are powered down.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Emulated off mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OFF_EMU
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    In Emulated off mode, the cluster behaves logically as if it were in the Off mode, except that the logic remains powered. The Debug state is retained and accessible.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Emulated memory retention mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MEM_RET_EMU
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     In Emulated memory retention mode, the cluster behaves logically as if it were in the Memory retention mode, except that the logic remains powered. The Debug state is retained and is accessible.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Warm reset mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WARM_RST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The Warm reset mode provides a Warm reset to all the
    <span>
     <span class="documents-keyword">
      DynamIQ&trade; cluster shared logic
     </span>
    </span>
    apart from the PPUs.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Debug recovery mode
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DBG_RECOV
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Debug recovery mode is used for applying a Warm reset to the cluster, while preserving memory and Reliability, Availability, and Serviceability (RAS) registers for debug purposes. Both L3 cache and RAS state are preserved when transitioning from DBG_RECOV mode to ON mode. Debug recovery mode is typically used in debugging a watchdog timeout.
    </p>
   </td>
  </tr>
 </tbody>
</table>
