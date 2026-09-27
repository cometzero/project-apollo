# Cross Trigger Channel interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Debug-and-Trace-Related-interfaces/Cross-Trigger-Channel-interface>

### Cross Trigger Channel interface

When DEBUGLEVEL > 0, CRSAS Ma1 includes one or more sets of Cross Trigger Channel inputs and Cross Trigger Channel outputs to allow partners to expand the cross trigger infrastructure as follows.

When HASCSS = 1, CRSAS Ma1 includes a shared Cross Trigger Matrix (CTM) and provides a single Cross Trigger Channel input and a single Cross Trigger Channel output to allow partners to expand the cross trigger infrastructure. See the table below.

For more information of the CTM, see Arm® CoreSight™ System-on-Chip SoC-600 Technical Reference Manual. This interface is synchronous to DEBUGDEBUGCLK, resides in the PD\_DEBUG power domain and nCOLDRESETDEBUG reset domain.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Cross Trigger Channel interface
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
   <th class="documents-nocellnorowborder" colspan="1" id="d97257e81" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d97257e85" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d97257e89" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d97257e93" rowspan="1">
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
       CTMCHANNELIN[3:0]
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Channel in port
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CTMCHANNELOUT[3:0]
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Channel out port
    </p>
   </td>
  </tr>
 </tbody>
</table>

When HASCSS = 0 where there can only be one CPU, the Cross Trigger Channel interfaces of the processor are provided as expansion interfaces, CPU0CTICHIN[3:0] and CPU0CTICHOUT[3:0]. For more information of these interfaces, see Arm® Cortex®-M55 Processor Technical Reference Manual and Arm® Cortex®-M85 Processor Technical Reference Manual.

- For Cortex-M55, these interfaces are synchronous to CPUCPU0CLK, and reside in the PD\_CPU0 power domain and in the nCOLDRESETCPU0 reset domain.
- For Cortex-M85, these interfaces are synchronous to DEBUGCPU0CLK, and reside in the PD\_DEBUG power domain and in the nCOLDRESETDEBUGCPU0 reset domain.

One or more of these interfaces must exist when DEBUGLEVEL > 0. Otherwise, this interface might not exist. If it does exist, it is tied or unused.
