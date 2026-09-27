# Basic power dependency control

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/Basic-power-dependency-control>

### Basic power dependency control

The following table shows the PDCM table and it shows how the PD\_SYS is affected by the power state of the other domains.

The table only includes dependency controls for only a single power domain, PD\_SYS, in the top row. The left column lists the Power dependency inputs. Power dependency inputs are either:

- The “ON” state of power domains in the system. For example, PD\_SYS\_ON means PD\_SYS is ON when asserted.
- Expansion Power Dependency Control Matrix Q-Channel signals, PDCMONQREQn and PDCMRETQREQn, that are driven by expansion logic from outside the subsystem indicating a keep-up request from external power domains.

“Conf” indicates that it is software configurable to be sensitive to the respective dependency input. For example, PD\_SYS can be software configured to be sensitive to the ON state of itself and all Expansion Power Control Dependency inputs. If a power domain is sensitive to an ON dependency input, it means that once the power domain being controlled is already ON, if any of the dependency inputs is ON or true, then the power domain remains ON. The exception is with the PDCMRETQREQn inputs, where, if a power domain is configured to be sensitive to these, the power domain maintains at least in a retention state. The PDCM is used primarily to define when a power domain should not enter a lower power state. It is not designed to support powering up of any power domain.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Power Dependency Matrix, for PILEVEL = 0
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d8356e83" rowspan="1">
    <p>
     Power Dependency Inputs/ Power Domain
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d8356e87" rowspan="1">
    <p>
     PD_SYS
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
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Conf
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_NPU&lt;m&gt;
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Y
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCMONQREQn[k]
     <sup>
      2
     </sup>
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
      2
     </sup>
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

1 PD\_NPU<m>\_ON row does not exist if NUMNPU = 0

2 PDCMONQREQn[k] and PDCMRETQREQn[k], where k is {0- <PDCMQCHWIDTH-1>}

Since PD\_SYS can be configured to be sensitive to itself, when set up by software to do so, PD\_SYS remains ON once it is ON.

The intention of the PDCM and all other sensitivity defined for each power domain is to allow, as much as possible for the power control of the System to be performed primarily using dynamic power transitions. This reduces the number of software interactions needed for system management and therefore improves its responsiveness and contributes to further power reduction.

At PILEVEL = 0, the desired power state of the system is defined in part of the CPU internal controls and states, and the choice between IWIC or EWIC. See [Controlling PD\_SYS power states](/documentation/102803/0000/Functional-Description/Power-Control-Infrastructure/Basic-level-power-infrastructure/BR-SYS-power-modes/Controlling-PD-SYS-Power-States?lang=en "Other than WARM_RST state, the BR_SYS bounded region provides the ability for the PD_CPU0EPU to enter a lower power state independently as long as the PD_SYS is ON. To control if the PD_CPU0EPU can remain ON or be allowed to enter the Retention (RET) or OFF state, software can use the register CPDLPSTATE.ELPSTATE in conjunction with the CPPWR.SU10 in the CPU as follows:").
