# PERIPHSPPPCEXP{0-3}

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPCEXP-0-3->

###

The Expansion Secure Privileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2 and 3 allow software to configure each Peripheral Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is allowed Secure privileged Access only or is allowed Secure Unprivileged access as well.

Each field defines this for an associated peripheral, by the following settings:

- ‘1’ Allow Secure unprivileged and privileged access.
- ‘0’ Allow Secure privileged access only.

These directly control the expansion signals on the Security Control Expansion interface. All four registers are similar and each register x, where x is from 0 to 3, is defined as seen in the Bit descriptions table.

### Configurations

This register implementation depends on the configuration of individual fields.

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
   PERIPHSPPPCEXP&lt;x&gt; bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d107707e119" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d107707e123" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d107707e127" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d107707e131" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d107707e135" rowspan="1">
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
     31:16
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
      0x0000
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     15:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PERIPHSPPPCEXP &lt;x&gt;
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Expansion &lt;x&gt; Secure Privileged Access Peripheral Interconnect Subordinate Peripheral Protection Control. Each bit i drives the output signal
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHPPPCEXP&lt;x&gt;[i]
      </span>
     </span>
     if PERIPHNSPPCEXP&lt;x&gt;. PERIPHNSPPCEXP&lt;x&gt;[i] is also LOW, where x is 0 to 3. The configuration option PERIPHPPCEXP&lt;x&gt;DIS defines if each bit within this register is actually implemented such that if PERIPHPPCEXP&lt;x&gt;DIS[i] = 1&rsquo;b1, then PERIPHSPPPCEXP&lt;x&gt;[i] is disabled and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
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
      0x0000
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
