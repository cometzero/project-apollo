# SECRESPCFG

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/SECRESPCFG>

### SECRESPCFG

The Security Violation Response Configuration Register is used to define the response to an access that causes security violation on the Bus Fabric.

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
   SECRESPCFG bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d84572e107" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84572e111" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84572e115" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84572e119" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d84572e123" rowspan="1">
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
     SECRESPCFG
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     This field configures the response in case of a security violation:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;0&rsquo;: Read-Zero Write Ignore
      </p>
     </li>
     <li>
      <p>
       &lsquo;1&rsquo;: Bus error
      </p>
     </li>
    </ul>
    <p>
     Some components, for example, the AHB Memory Protection Controllers (MPC), provide their own control registers to configure their own response. Components that have their own register to control funtonality do not have to use this register.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
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
