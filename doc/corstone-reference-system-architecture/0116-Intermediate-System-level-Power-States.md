# Intermediate System level Power States

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/Intermediate-System-level-Power-States>

### Intermediate System level Power States

Through the relationship defined by Power dependency control matrix, and the CPU minimum power states, we can define several System Power States that the system supports.

SYS\_OFF
:   All voltage and power domains are OFF.

HIBERNATION0
:   The VSYS voltage domain is ON, and the system is in the lowest power state that can still be woken from sleep. At wake, the system has to reboot.

SYS\_RET
:   The system is in retention, and at wake, the system can continue to execute since no system state is lost.

SYS\_ON
:   The system is ON.

The following table lists the power states of each power domain that each of the System Power State supports or requires. See [Controlling PD\_CPU<n> power states](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-CPU-n--power-modes/Controlling-PD-CPU-n--power-states?lang=en "For the PD_CPU<n> to enter a lower power state, software on the CPU<n> must first configure its CPDLPSTATE.CLPSTATE register to define what power state CPU<n> can enter when in a sleep state as follows:").

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   System Level Power States when PILEVEL = 1
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
   <th class="documents-nocellnorowborder" colspan="1" id="d149238e106" rowspan="2">
    <p>
     Power Domains
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="4" id="d149238e110" rowspan="1">
    <p>
     System Level Power States
    </p>
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d149238e117" rowspan="1">
    <p>
     SYS_OFF
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d149238e121" rowspan="1">
    <p>
     HIBERNATION0
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d149238e125" rowspan="1">
    <p>
     SYS_RET
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d149238e129" rowspan="1">
    <p>
     SYS_ON
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     VSYS (PD_AON)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_SYS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RET
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU&lt;n&gt;
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF &ndash; DeepSleep
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF - DeepSleep
    </p>
    <p>
    </p>
    <p>
     RET - DeepSleep
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     OFF &ndash; DeepSleep
    </p>
    <p>
    </p>
    <p>
     RET &ndash; DeepSleep
    </p>
    <p>
    </p>
    <p>
     ON &ndash; DeepSleep
    </p>
    <p>
    </p>
    <p>
     ON &ndash; Sleep
    </p>
    <p>
    </p>
    <p>
     ON
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_NPU&lt;m&gt;
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     OFF/ON
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_DEBUG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF/ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF/ON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     OFF/ON
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CRYPTO
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     OFF/ON
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PD_VMR&lt;i&gt;
     <sup>
      4
     </sup>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     OFF
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     OFF/RET
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     OFF/RET
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     OFF/RET/ON
    </p>
   </td>
  </tr>
 </tbody>
</table>

1 When the CPU<n> and therefore PD\_SYS is in OFF-DeepSleep state, PD\_VMR<i> can either be OFF or be in retention and is defined by CPU<n>PWRCFG.TCM\_MIN\_PWR\_STATE. In this state, the EPU must be OFF. The PD\_CPU<n>RAM can be OFF permanently and is defined by CPUPWRCFG.TCM\_MIN\_PWR\_STATE.

2 This power domain only exists when HASCRYPTO = 1.

3 These power domains only exist when NUMNPU > 0.

4 This power domain only exists if NUMVMBANK > 0.

The following points can be made based on the preceding table:

- The System Level Power States are closely associated with the PD\_SYS power states, PD\_CPU<n>EPU and PD\_CPU<n>RAM, and PD\_VMR<i> supported states are associated with PD\_SYS states. See the figure in [BR\_SYS power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-SYS-power-modes?lang=en "The following figure shows the power modes that BR_SYS supports.").
- Generally, PD\_DEBUG can be woken independently except in the SYS\_OFF state.
- Memory power states, PD\_VMR, are defined as part of BR\_SYS and cannot be controlled independently from PD\_SYS.

An additional transient WARM\_RST state also exists for the system when a Warm reset is being performed. This state can only be entered from SYS\_ON state. In this state, all power domains, except PD\_AON, temporarily enter WARM\_RST mode and exit it when Warm reset is completed.
