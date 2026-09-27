# Other Security Expansion signals

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/Security-Control-Expansion-signals/Other-Security-Expansion-signals>

### Other Security Expansion signals

The following table lists other signals that are related to Security that is needed by PPCs and MSCs in the expansion system.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Other Security Expansion signals
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
   <th class="documents-nocellnorowborder" colspan="1" id="d92624e61" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92624e65" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d92624e69" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d92624e73" rowspan="1">
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
       SECRESPCFG
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This output configures how to respond to an access when a security violation occurs.
    </p>
    <ul>
     <li>
      <p>
       0: Read-Zero Write Ignore
      </p>
     </li>
     <li>
      <p>
       1: Bus error
      </p>
     </li>
    </ul>
    <p>
     This output is controlled by the SECRESPCFG register.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       ACCWAITn
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This request output is used to control any external gating unit that may be required to block accesses to the system through the Main and Peripheral Interconnect Expansion interfaces.
    </p>
    <ul>
     <li>
      <p>
       1: No gating
      </p>
     </li>
     <li>
      <p>
       0: Access gated
      </p>
     </li>
    </ul>
    <p>
     This output is controlled by the BUSWAIT register.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       ACCWAITNSTATUS
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Input
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     This status output is used to indicate the current state of any external gating unit that may be used to block access to the system through the Main and Peripheral Interconnect Expansion interfaces
    </p>
    <ul>
     <li>
      <p>
       1: No gating
      </p>
     </li>
     <li>
      <p>
       0: Access gated
      </p>
     </li>
    </ul>
    <p>
     This input can be read using the BUSWAIT register.
    </p>
   </td>
  </tr>
 </tbody>
</table>
