# Intermediate power dependency control

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/Intermediate-power-dependency-control>

### Intermediate power dependency control

The following table shows the PDCM table and it shows how the PD\_SYS and PD\_VMR<i> are affected by the power state of the other domains.

The heading row of the table lists the Power Domains that are being controlled, while the left column lists the Power dependency inputs. Power dependency inputs are either:

- The “ON” state of power domains in the system. For example, PD\_SYS\_ON means PD\_SYS is ON when asserted.
- Expansion Power Dependency Control Matrix Q-Channel Signals, PDCMONQREQn and PDCMRETQREQn, that are driven by expansion logic from outside the subsystem indicating a keep-up request from external power domains.

“Conf” indicates that the power domain is software configurable while “Y” indicates that it is always sensitive to the respective dependency input. For example, PD\_SYS can be software configured to be sensitive to the ON state of PD\_SYS and all Expansion Power Control Dependency inputs, and it is always sensitive to the ON state of all PD\_CPU<n>, PD\_NPU<m> and PD\_CRYPTO. If a power domain is sensitive to an ON dependency input, it means that once the power domain being controlled is already ON, if any of the dependency inputs is ON or true, then the power domain remains ON. The exception is with the PDCMRETQREQn inputs, where, if a power domain is configured to be sensitive to these, the power domain maintains at least in a retention state. The PDCM is used primarily to define when a power domain should not enter a lower power state. It is not designed to support powering up of any power domain.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Power Dependency Matrix for PILEVEL = 1
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
   <th class="documents-nocellnorowborder" colspan="1" id="d18081e98" rowspan="1">
    <p>
     Power Dependency Inputs/ Power Domain
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18081e102" rowspan="1">
    <p>
     PD_SYS
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18081e106" rowspan="1">
    <p>
     PD_VMR0
     <sup>
      1
     </sup>
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18081e112" rowspan="1">
    <p>
     PD_VMR1
     <sup>
      1
     </sup>
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18081e118" rowspan="1">
    <p>
     PD_VMR2
     <sup>
      1
     </sup>
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d18081e125" rowspan="1">
    <p>
     PD_VMR3
     <sup>
      1
     </sup>
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_SYS_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU0_ON
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU1_ON
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU2_ON
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU3_ON
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_NPU0_ON
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_NPU1_ON
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_NPU2_ON
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_NPU3_ON
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CRYPTO_ON
     <sup>
      4
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCMONQREQn[k]
     <sup>
      5
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PDCMRETQREQn[k]
     <sup>
      5
     </sup>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
 </tbody>
</table>

1 PD\_VMR<i> columns do not exist if i > (NUMVMBANK – 1)

2 PD\_CPU<n>\_ON row does not exist if n > NUMCPU

3 PD\_NPU<m>\_ON row does not exist if NUMNPU = 0

4 PD\_CRYPTO<n>\_ON row does not exist if HASCRYPTO = 0

5 PDCMONQREQn[k] and PDCMRETQREQn[k], where k is {0- <PDCMQCHWIDTH-1>}

PD\_VMR<i> can also be configured to be sensitive to a power domain. For example, if PD\_VMR0 sensitivity is configured by software to be sensitive to PD\_CPU0\_ON, and if PD\_CPU0 is ON, the memory also remains ON. However, PD\_VMR0 is controlled using the same PPU as PD\_SYS and as a result of the power state of the PPU shown in the figure in [BR\_SYS power modes](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Intermediate-level-power-infrastructure/BR-SYS-power-modes?lang=en "The following figure shows the power modes that BR_SYS supports."), whenever PD\_VMR0 is ON, PD\_SYS also remains in one of the ON\_OPMODE states where PD\_VMR0 is ON.

> ### Note
>
> PD\_SYS can be configured to be sensitive to itself. When software configures a domain to be sensitive to self, the domain remains ON once it is ON.

The intention of the PDCM and all other sensitivity defined for each power domain is to allow, as much as possible for the power control of the System to be performed primarily using dynamic power transitions. This reduces the number of software interactions needed for system management and therefore improves its responsiveness and contributes to further power reduction.

CRSAS Ma1 also provides a programmable register for the power domains shown in the following table, which defines the lowest power mode that each domain can enter. PD\_NPU<m> and PD\_DEBUG defaults to a minimum power state of OFF.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Power Domain&rsquo;s Minimum Power State for PILEVEL = 1
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d18081e586" rowspan="1">
    <p>
     Power Domain
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d18081e590" rowspan="1">
    <p>
     Supported MIN_PWR_STATE for each domain
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_SYS
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     ON, OFF, Retention,
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PD_VMR&lt;i&gt;
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     ON, OFF, Retention
    </p>
   </td>
  </tr>
 </tbody>
</table>

The MIN\_PWR\_STATEs of both PD\_SYS and PD\_VMR<i> therefore help to determine which power modes of the BR\_SYS PPU can be used next when performing dynamic power transition.

For example, if the system is idle and all dependent domains are not ON, and then the BR\_SYS PPU try to enter the bounded domain collectively to a low-power state, if MIN\_PWR\_STATE of PD\_SYS is set to Retention, then BR\_SYS is never allowed to enter the OFF state nor any of the MEM\_RET\_OPMODE<x> states because PS\_SYS is not allowed to turn off. Then, depending on the current PD\_VMR<i> states, it tries to enter one of the associated FULL\_RET\_OPMODE<x> states.

In another example, if PDCM\_PD\_VMR<x>\_SENSE.MIN\_PWR\_STATE of PD\_VMR0 is “ON” and all other PD\_VMRs are OFF, then if currently all PD\_VMR<i> are ON, when BR\_SYS PPU is entering a low-power state, it transitions to ON\_OPMODE1 state to turn off all PD\_VMR<i> except PD\_VMR0. It never enters FULL\_RET\_OPMODE1 nor MEM\_RET\_OPMODE1.
