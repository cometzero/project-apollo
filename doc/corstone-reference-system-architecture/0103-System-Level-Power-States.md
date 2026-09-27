# System Level Power States

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Advanced-level-power-infrastructure/System-Level-Power-States>

### System Level Power States

Through the relationship defined by the Power dependency control matrix, the MIN\_PWR\_STATEs of each power domain, and the CPU minimum power states, we can define several System Power States that the system supports.

SYS\_OFF
:   All voltage and power domains are OFF.

HIBERNATION1
:   The VSYS voltage domain maybe ON or OFF, and the system is in the lowest power state that can still be woken from sleep. At wake, the system has to reboot.

HIBERNATION0
:   The VSYS voltage domain is ON, and the system is in the second lowest power state where PD\_MGMT is still ON. The system can be woken from sleep, potentially quicker than from HIBERNATION1. At wake, the system has to reboot.

SYS\_RET
:   The system is in retention, and at wake, the system can continue to execute since no system state is lost.

SYS\_ON
:   The system is ON.

The following table lists the power states of each power domain that each of the System Power State supports or requires. See [Controlling PD\_CPU<n> power states](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-CPU-n--power-modes/Controlling-PD-CPU-n--power-states?lang=en "For the PD_CPU<n> to enter a lower power state, software on the CPU<n> must first configure its CPDLPSTATE.CLPSTATE register to define what power state CPU<n> can enter when in a sleep state as follows:") in [BR\_CPU<n> power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-CPU-n--power-modes?lang=en "The following figure shows the power modes that BR_CPU<n> supports.").

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   System Level Power States
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d40177e123" rowspan="2">
    <p>
     Power Domains
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="5" id="d40177e127" rowspan="1">
    <p>
     System Level Power States
    </p>
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d40177e134" rowspan="1">
    <p>
     SYS_OFF
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d40177e138" rowspan="1">
    <p>
     HIBERNATION1
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d40177e142" rowspan="1">
    <p>
     HIBERNATION0
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d40177e146" rowspan="1">
    <p>
     SYS_RET
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d40177e150" rowspan="1">
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
     VAON (PD_AON)
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
     PD_MGMT
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
     OFF - DeepSleep
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
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     OFF/RET
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     OFF/ON
    </p>
   </td>
  </tr>
 </tbody>
</table>

1 This power domain only exists when HASCRYPTO = 1.

2 When CPU<n> is in OFF-DeepSleep state, the TCM associated with that CPU can either be OFF or be in retention and is defined by CPUPWRCFG.TCM\_MIN\_PWR\_STATE. In this state, the EPU must be OFF. The PD\_CPU<n>RAM can be OFF permanently and is defined by CPDLPSTATE.RLPSTATE.

3 These power domains only exist when NUMNPU > 0.

4 This power domain only exists if NUMVMBANK > 0.

The following points can be made based on the preceding table:

- When PD\_CRYPTO is ON, PD\_SYS must also be ON and therefore PD\_MGMT is also ON.
- When PD\_NPU<m> is ON, PD\_SYS must also be ON and therefore PD\_MGMT is also ON.
- When waking up any of the PD\_CPU<n> or PD\_CRYPTO power domains, if the PD\_SYS is OFF or RET, it always also automatically wakes the PD\_SYS domain to ON since PD\_CPU<n> ON and PD\_CRYPTO ON states are only supported in SYS\_ON System Power State. This means that PD\_MGMT also automatically turns ON.
- In the HIBERNATION0, PD\_MGMT is ON and PD\_DEBUG and can be woken independently.
- In the HIBERNATION1, PD\_MGMT is OFF. Anything that wakes the system must also wake PD\_MGMT.
- PD\_VMR<i> is tied to PD\_SYS because they belong to the bounded region BR\_SYS. You are not able to wake PD\_VMR<i> independently from PD\_SYS.

An additional transient WARM\_RST state exists for the system when a Warm reset is being performed. This state can only be entered from SYS\_ON state. In this state, all power domains, except PD\_AON, temporarily enter WARM\_RST mode and exit it when Warm reset is completed.

> ### Note
>
> When PD\_MGMT is OFF, VSYS can also turn OFF. However, in some scenarios depending on implementation or integration, VSYS can remain ON if VAON is also ON.
