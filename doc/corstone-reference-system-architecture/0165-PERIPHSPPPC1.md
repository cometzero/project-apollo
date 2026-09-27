# PERIPHSPPPC1

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC1>

### PERIPHSPPPC1

Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:

- ‘1’: Allow Secure Unprivileged and privileged access.
- ‘0’: Allow Secure privileged access only.

CRSAS Ma1 has two such registers, see also [PERIPHSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC0?lang=en "Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:").

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
   PERIPHSPPPC1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d93357e124" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d93357e128" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d93357e132" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d93357e136" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d93357e140" rowspan="1">
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
     31:2
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
     SP_SLOWCLK_TIMER
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Secure privileged setting for SLOWCLK_TIMER.
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
