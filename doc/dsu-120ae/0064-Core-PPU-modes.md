# Core PPU modes

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Core-PPU-modes>

### Core PPU modes

Each core or complex in the DSU-120AE DynamIQ™ cluster has a defined set of Power Policy Unit (PPU) modes and corresponding legal transitions between these modes. The PPU mode of each core can be independent of other cores in a cluster.

> ### Note
>
> - As there are no operating modes for the cores in the DSU-120AE DynamIQ™ cluster, the core PPU modes are equivalent to core power modes. However, they are called core PPU modes to be consistent with the terminology for programming the PPU.
> - Some types of core might not support all the PPU (power) modes. See your core Technical Reference Manual (TRM) to see which PPU modes are supported.

The following table shows all the possible PPU modes supported by the cores.

<table id="kuk1660577239456__table_egd_ltt_4t">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   <span>
    Core
   </span>
   <span>
    <span class="documents-keyword">
     PPU modes
    </span>
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
   <th class="documents-row-nocellborder" colspan="1" id="d100517e155" rowspan="1">
    <span>
     <span class="documents-keyword">
      PPU mode
     </span>
    </span>
   </th>
   <th class="documents-row-nocellborder" colspan="1" id="d100517e160" rowspan="1">
    Short name
   </th>
   <th class="documents-row-nocellborder" colspan="1" id="d100517e163" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     On
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     The
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     is powered up and active.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Functional retention
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     FUNC_RET
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     The
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     is fully powered and operational, but the Vector Processing Unit (VPU), if present, is OFF.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Full retention
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     FULL_RET
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     The
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     is in retention state.
    </p>
    <p>
     In this mode, only power that is required to retain register and RAM state is available. The
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     is non-operational.
    </p>
    <p>
     If the
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     supports functional retention and functional retention is enabled, then the
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     must be in Functional retention mode before it enters this mode.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Off
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     The
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     is powered down, either by using internal power switches or externally by the voltage regulator.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Emulated off
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     OFF_EMU
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     On mode, with Warm reset asserted. Debug state is retained and accessible.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Debug recovery
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DBG_RECOV
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The RAM and logic are powered up.
    </p>
    <p>
     This mode is for applying a Warm reset to the cluster, while preserving memory and RAS registers for debug purposes. Both cache and Reliability, Availability, and Serviceability (RAS) state are preserved when transitioning from DBG_RECOV to ON.
    </p>
    <blockquote title="Note warning">
     <h3 class="documents-underline">
      CAUTION
     </h3>
     This mode must not be used during normal system operation.
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Warm reset
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    WARM_RST
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    This Warm reset mode is used to reset the
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    . For more information about what is reset, see your
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    Technical Reference Manual (TRM).
   </td>
  </tr>
 </tbody>
</table>
