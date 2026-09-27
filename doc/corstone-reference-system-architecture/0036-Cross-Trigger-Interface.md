# Cross Trigger Interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Debug-and-Trace-Related-interfaces/Cross-Trigger-Interface>

### Cross Trigger Interface

When DEBUGLEVEL > 0 and HASCSS > 0, CRSAS Ma1 includes a shared Cross Trigger Interface (CTI) module. Some trigger signals to and from the CTI are used within the system, while a number is made available to system expansion. The following table lists the trigger signals that are available for system expansion.

For more information on the CTI, see Arm® CoreSight™ System-on-Chip SoC-600 Technical Reference Manual.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTI triggers
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
   <th class="documents-nocellnorowborder" colspan="1" id="d95839e72" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95839e76" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d95839e80" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d95839e84" rowspan="1">
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
       CTIEVENTIN[7:4]
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
     CTI Trigger inputs
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CTIEVENTOUT[7:6]
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     CTI Trigger outputs
    </p>
   </td>
  </tr>
 </tbody>
</table>

This interface is synchronous to DEBUGDEBUGCLK, resides in the PD\_DEBUG power domain and nCOLDRESETDEBUG reset domain.

This interface must exist when DEBUGLEVEL > 0 and HASCSS = 1. Otherwise, this interface might not exist and if it does, it is tied or unused.
