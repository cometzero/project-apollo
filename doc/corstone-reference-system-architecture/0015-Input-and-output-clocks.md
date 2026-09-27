# Input and output clocks

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Input-and-output-clocks>

### Input and output clocks

The following table lists all the clock inputs into the subsystem.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CRSAS Ma1 input clocks
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d42151e59" rowspan="1">
    <p>
     Clock Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d42151e63" rowspan="1">
    <p>
     Target Power
     <sup>
      1
     </sup>
     Domain PILEVEL= 2
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d42151e70" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Slow Clock. An always active slow clock input that is completely asynchronous to the other clocks in the system. This is one of the only two clocks expected to be active in the lowest power state of the system, HIBERNATE{0,1}, and is used primarily by timers that reside in the PD_AON domain.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AONCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Always ON Clock Input. This clock is used for logic in the PD_AON domain that is not running on
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     . This allows the rest of the PD_AON domain to run on a faster clock and yet be independent from the rest of the system.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CNTCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Counter Timestamp Clock associated with the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CNTVALUE&lt;G/B&gt;
      </span>
     </span>
     System Counter Timestamp input.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_MGMT
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Main System Clock Input. This clock is the main clock used to drive the main system that resides in PD_SYS. This clock is also used for logic in the PD_MGMT domain if it exists, or logic that is merged from PD_MGMT to PD_AON if PILEVEL &lt; 2.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       DEBUGCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_DEBUG
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Debug System Clock Input. This clock is used to drive all logic in the debug System. This input clock must exist when HASCSS = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU&lt;n&gt;
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU clock. This is the clock used to drive each CPU.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NPU&lt;m&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PD_NPU&lt;m&gt;
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     NPU clock. This is the clock used to drive each NPU. This clock only exists if NUMNPU &gt; 0.
    </p>
   </td>
  </tr>
 </tbody>
</table>

1 When PILEVEL = 0, power domains are merged as follows:

- PD\_MGMT is merged with PD\_AON and all reference to PD\_MGMT is replaced by PD\_AON.
- PD\_CPU<n> is merged with PD\_SYS and all reference to PD\_CPU<n> is replaced by PD\_SYS.

2 When PILEVEL = 1, power domains are merged as follows:

- PD\_MGMT is merged with PD\_AON and all reference to PD\_MGMT is replaced by PD\_AON.

The relation between these clocks is IMPLEMENTATION DEFINED with the architecture able to support all clocks being completely asynchronous to each other. However, during implementation, to reduce the number of clock sources, the implementor, or the SoC Integrator can drive several clocks using the same clock sources, so long as the implementor takes clock availability, power and response time into consideration.

In typical use, we recommend that SLOWCLK is driven using a 32kHz clock source. If reducing standby power is an important consideration for a product, AONCLK can be driven at a lower clock rate (around 1MHz to 10MHz) compared to SYSCLK to improve the transition time entering and leaving the lowest power state of the system, but still support the use of very low leakage implementation library cells. Alternatively, AONCLK can be driven using the same clock source as SYSCLK. If there is no requirement to run the processors and System Timestamp Counter at a different speed to the system, then CPU<n>CLK and CNTCLK can also be driven using the same clock source as SYSCLK. DEBUGCLK can also be driven using the same clock as CPU<n>CLK. NPU<m>CLK may be driven from the same clock source as SYSCLK

At a minimum, only two clock sources are needed. For example, one at 32KHz for SLOWCLK and another at 200MHz for the rest. If for example, very large SRAMs with higher access time are needed in the system, SYSCLK could be clocked synchronously to and at a fixed fraction of CPU<n>CLK.

The following table also shows for each clock the target power domain that clock is expected to be used.

> ### Note
>
> All clocks always first enter either through the PD\_AON domain before being used in their respective power domain.

The following table lists all the clock outputs from the subsystem.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   CRSAS Ma1 output clocks
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d42151e318" rowspan="1">
    <p>
     Clock Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d42151e322" rowspan="1">
    <p>
     Power Domain expected to be used in
     <sup>
      1
     </sup>
    </p>
    PILEVEL = 2
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d42151e329" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MGMTSYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_MGMT
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Gated version of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
     expected to be used to drive expansion logic that resides in the PD_MGMT power domain when PILEVEL = 2.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSSYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_SYS
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Gated version of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
     expected to be used to drive expansion logic that resides in the PD_SYS power domain.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       DEBUGDEBUGCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_DEBUG
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Gated version of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       DEBUGCLK
      </span>
     </span>
     expected to be used to drive debug expansion logic that resides in the PD_DEBUG power domain. This output clock must exist when HASCSS = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPUCPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_CPU&lt;n&gt;
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Gated version of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
     expected to be used to drive expansion logic that resides in the PD_CPU&lt;n&gt; powerdomain.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       DEBUGCPU&lt;n&gt;CLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_DEBUG
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Gated version of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
     expected to be used to drive debug expansion logic that resides in the PD_DEBUG power domain. This output clock must exist when HASCSS = 0.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CRYPTOSYSCLK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PD_CRYPTO
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Gated version of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
     expected to be used to drive expansion logic that resides in the PD_CRYPTO power domain. This clock must exist when HASCRYPTO = 1.
    </p>
   </td>
  </tr>
 </tbody>
</table>

1 When PILEVEL = 0, power domains are merged as follows:

- PD\_MGMT is merged with PD\_AON and all reference to PD\_MGMT is replaced by PD\_AON.
- PD\_CPU<n> is merged with PD\_SYS and all reference to PD\_CPU<n> is replaced by PD\_SYS.
- PD\_CRYPTO is merged with PD\_SYS and all reference to PD\_CRYPTO, if exist, is replaced by PD\_SYS.

When PILEVEL = 1, power domains are merged as follows:

- PD\_MGMT is merged with PD\_AON and all reference to PD\_MGMT is replaced by PD\_AON,
- PD\_CRYPTO is merged with PD\_SYS and all reference to PD\_CRYPTO, and all references to PD\_CRYPTO are replaced by PD\_SYS.

CRSAS Ma1 provides a Q-Channel interface for each of the output clocks to allow expansion logic to control the availability of each clock output, see [Clock control Q-Channel device interfaces](/documentation/102803/0000/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces/Clock-control-Q-Channel-device-interfaces?lang=en "CRSAS Ma1 defines a Q-Channel Device interface for each of the output clocks to allow expansion logic to control the availability of each clock output. These are used to support high-level clock gating. Each interface can either be single bit or a vector, and is IMPLEMENTATION DEFINED.").
