# SPCSECCTRL

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/SPCSECCTRL>

### SPCSECCTRL

The Security Privilege Controller Security Configuration Control Register implements the security lock register.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Power domain
:   PD\_SYS

Reset
:   This register is reset by
    nWARMRESETSYS.

### Usage constraints

This register is Secure Privileged access only and supports 32-bit RW accesses. For write access to this register, only 32-bit writes are supported. Any byte and halfword writes are ignored.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SPCSECCTRL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d21219e107" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21219e111" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21219e115" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21219e119" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d21219e123" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     31:1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     SPCSECCFGLOCK
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Active-HIGH Control to Disable writes to Security related control registers in the Secure Access Configuration Register Block. Once set to HIGH, it can no longer be cleared to zero except through reset or the PD_SYS turning OFF. Registers that can no longer be modified when SPCSECCFGLOCK is set to HIGH are:
    </p>
    <ul>
     <li>
      <p>
       NSCCFG
      </p>
     </li>
     <li>
      <p>
       MAINNSPPC0
      </p>
     </li>
     <li>
      <p>
       MAINNSPPCEXP&lt;i&gt;
      </p>
     </li>
     <li>
      <p>
       PERIPHNSPPC0
      </p>
     </li>
     <li>
      <p>
       PERIPHNSPPC1
      </p>
     </li>
     <li>
      <p>
       PERIPHNSPPCEXP&lt;i&gt;
      </p>
     </li>
     <li>
      <p>
       MAINSPPPC0
      </p>
     </li>
     <li>
      <p>
       MAINSPPPCEXP&lt;i&gt;
      </p>
     </li>
     <li>
      <p>
       PERIPHSPPPC0
      </p>
     </li>
     <li>
      <p>
       PERIPHSPPPC1
      </p>
     </li>
     <li>
      <p>
       PERIPHSPPPCEXP&lt;i&gt;
      </p>
     </li>
     <li>
      <p>
       NSMSCEXP
      </p>
     </li>
     <li>
      <p>
       NPUSPPORSL
      </p>
     </li>
     <li>
      <p>
       NPUSPPORPL
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW1S
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
