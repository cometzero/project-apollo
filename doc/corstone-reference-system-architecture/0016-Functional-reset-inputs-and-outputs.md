# Functional reset inputs and outputs

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Functional-reset-inputs-and-outputs>

### Functional reset inputs and outputs

Reset inputs are used to drive or to request for resets while reset outputs are used to reset expansion logic that resides in specific power domains. For more information, see [Reset infrastructure](/documentation/102803/0000/Functional-Description/Reset-infrastructure?lang=en "CRSAS Ma1 defines the following system level reset scopes, namely:").

Unless explicitly stated, it is IMPLEMENTATION DEFINED if these resets are asynchronous or synchronous. We recommend that all resets are asynchronously asserted and synchronously deasserted in relation to the reset domain’s clock, except for reset requests that end with the “REQ” suffix.

The following table lists all the reset interfaces on the subsystem.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Reset signals
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
   <th class="documents-nocellnorowborder" colspan="1" id="d129028e78" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d129028e82" rowspan="1">
    <p>
     Power Domain where it is used when
     <sup>
      1
     </sup>
     PILEVEL = 2
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d129028e89" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d129028e93" rowspan="1">
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
       nPORESET
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Power-On Reset Input.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nSRST
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Cold Reset request Input from Debugger.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       HOSTRESETREQ
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Higher Authority request to perform a Cold reset, for example from a hosting system. This is an asynchronous input. This reset request always results in a system Cold reset regardless of the COLDRESET_MODE configuration. After it is asserted, the signal must be held high until the reset occurs on
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETAON
      </span>
     </span>
     . Holding this input HIGH also results in the system being held in Cold reset.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       RESETREQ
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active-HIGH Hardware Request Input to perform a Cold reset. This is an asynchronous input. After it is asserted, the signal must be held HIGH until the reset occurs on
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETAON
      </span>
     </span>
     . The signal must be cleared because of the assertion of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETAON
      </span>
     </span>
     . When COLDRESET_MODE = 1, this input has no effect on Cold reset directly.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       EXPWARMRESETREQ
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active-HIGH Request to expansion logic to prepare for a Warm reset. This input is associated with
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       EXPWARMRESETACK
      </span>
     </span>
     . This signal is an asynchronous output. The existence of this signal and the associated acknowledge signal is
     <span class="documents-archterm">
      IMPLEMENTATION DEFINED
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       EXPWARMRESETACK
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active-HIGH Acknowledge for expansion logic to indicate that it is ready for Warm reset. This input is associated with
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       EXPWARMRESETREQ
      </span>
     </span>
     . This is an asynchronous input. The existence of this signal and the associated request signal is
     <span class="documents-archterm">
      IMPLEMENTATION DEFINED
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETAON
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Cold Reset for the Expansion System. This Cold reset merges other reset sources within the system with
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nPORESET
      </span>
     </span>
     to generate this reset in the PD_AON domain. This reset is expected to be used in the PD_AON domain.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nWARMRESETAON
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Warm reset for the Expansion System. This Warm reset is generated by combining Warm reset requests from the system along with Cold reset in the PD_AON domain. This reset is expected to be used in the PD_AON domain
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETMGMT
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Cold reset for the PD_MGMT power domain. This reset is expected to be used in the PD_MGMT domain.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nWARMRESETMGMT
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Warm reset for the PD_MGMT power domain. This reset is expected to be used in the PD_MGMT domain.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETSYS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_SYS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Cold reset for the PD_SYS power domain. This reset is expected to be used in the PD_SYS domain.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nWARMRESETSYS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_SYS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Warm reset for the PD_SYS power domain. This reset is expected to be used in the PD_SYS domain.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETDEBUG
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_DEBUG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Cold reset for the PD_DEBUG power domain. This reset is expected to be used in the PD_DEBUG domain. This output must exist when HASCSS = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nWARMRESETCRYPTO
      </span>
     </span>
    </p>
   </td>
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
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Cold reset for the PD_CRYPTO power domain. This reset is expected to be used in the PD_CRYPTO domain. This reset must exist when HASCRYPTO = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nWARMRESETCPU&lt;n&gt;
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Warm reset for each of the PD_CPU&lt;n&gt; power domain. These resets are expected to be used in the PD_CPU&lt;n&gt; domains.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETCPU&lt;n&gt;
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Cold reset for each of the PD_CPU&lt;n&gt; power domain. These resets are expected to be used in the PD_CPU&lt;n&gt; domains.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETDEBUGCPU&lt;n&gt;
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PD_DEBUG
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Active LOW Cold reset for PD_DEBUG associated with the debug logic of each CPU. These are expected to be used in the PD_DEBUG domain.
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
- PD\_MGMT is merged with PD\_AON and all reference to PD\_MGMT is replaced by PD\_AON.
- PD\_CRYPTO is merged with PD\_SYS and all reference to PD\_CRYPTO, if exist, is replaced by PD\_SYS.
