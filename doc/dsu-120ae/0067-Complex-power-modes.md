# Complex power modes

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Complex-power-management/Complex-power-modes>

### Complex power modes

For a complex containing two cores, a Power Policy Unit (PPU) mode change to either of the cores requires some arbitration between the cores in the complex and the shared logic. This is carried out automatically by the complex bridge, without involvement of the core PPU.

For cores outside a complex with a CPU bridge, the power mode being requested by the PPU can be directly applied. When the CPU bridge interfaces with a complex, there might be multiple cores and some shared logic such as L2 cache and a Vector Processing Unit (VPU). The complex bridge handles system requests for power mode transitions by translating requests into the correct power mode transitions for a particular complex configuration.

The following table shows an example of all possible combinations of input requests and corresponding power transitions for a dual-core complex with a shared L2 cache and VPU.

<table id="bzd1660577241616__table_complex_power_modes">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU mode and power domain states for a dual-
   <span>
    <span class="documents-keyword">
     core
    </span>
   </span>
   complex
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
   <th class="documents-nocellnorowborder" colspan="2" id="d130752e135" rowspan="1">
    Requested PPU mode
   </th>
   <th class="documents-nocellnorowborder" colspan="3" id="d130752e138" rowspan="1">
    PCSM channel
   </th>
  </tr>
  <tr>
   <th class="documents-row-nocellborder" colspan="1" id="d130752e144" rowspan="1">
    Core0
   </th>
   <th class="documents-row-nocellborder" colspan="1" id="d130752e147" rowspan="1">
    Core1
   </th>
   <th class="documents-row-nocellborder" colspan="1" id="d130752e150" rowspan="1">
    Core0
   </th>
   <th class="documents-row-nocellborder" colspan="1" id="d130752e153" rowspan="1">
    Core1
   </th>
   <th class="documents-row-nocellborder" colspan="1" id="d130752e156" rowspan="1">
    Shared logic
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    On
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Functional retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Full retention
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Debug recovery
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Emulated off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ON
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Off
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OFF
   </td>
  </tr>
 </tbody>
</table>

> ### CAUTION
>
> Deviating from the legal power modes can lead to
> unpredictable results. You must comply with the dynamic power management and powerup and powerdown sequences, see your
> core Technical Reference Manual.
