# MAINNSPPPC0

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPC0>

### MAINNSPPPC0

Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each peripheral on the Main Interconnect that it controls through a PPC is only allowed Non-secure Privileged Access or is allowed Non-secure Unprivileged access as well.

Each field defines this for an associated peripheral, by the following settings:

- ‘1’: Allow Non-secure unprivileged and privileged access
- ‘0’: Allow Non-secure privileged access only

CRSAS Ma1 currently does not have any Main Interconnect subordinate interfaces that need Non-secure Unprivileged Access configuration support of the PPC. Therefore, this register is reserved.

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

This register is Non-secure privileged access only and supports 32-bit RW accesses. For write access to this register, only 32-bit writes are supported. Any byte and halfword writes are ignored.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MAINNSPPPC0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d43752e119" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43752e123" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43752e127" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d43752e131" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d43752e135" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     31:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Reserved.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
