# MAINNSPPPCEXP{0-3}

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/MAINNSPPPCEXP-0-3->

###

The Expansion Non-secure Unprivileged Access Main Interconnect Subordinate Peripheral Protection Controller registers 0, 1, 2 and 3 allow software to conﬁgure each Main Interconnect peripheral that it controls through each PPC, that resides in the expansion logic outside the subsystem, is only Non-secure privileged Access or is allowed Non-secure Unprivileged access as well.

Each field defines this for an associated peripheral, by the following settings:

- ‘1’: Allow Non-secure unprivileged and privileged access
- ‘0’: Allow Non-secure privileged access only

These settings directly control the expansion signals on the Security Control Expansion interface. All four register are similar and each register, x where x is from 0 to 3 is as seen in the Bit descriptions table.

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

This register is Non-secure privileged access only and supports 32-bit RW accesses. For write access to this register, only 32-bit writes are supported. Any byte and halfword writes are ignored.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MAINNSPPPCEXP&lt;x&gt; bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d42985e119" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d42985e123" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d42985e127" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d42985e131" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d42985e135" rowspan="1">
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
     MAINNSPPPCEXP &lt;x&gt;
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Expansion &lt;x&gt; Non-secure Privileged Access Main Interconnect Subordinate Peripheral Protection Control. Each bit i drives the output signal
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINPPPCEXP&lt;x&gt;[i]
      </span>
     </span>
     if MAINSPPPCEXP&lt;x&gt;. MAINNSPPCEXP&lt;x&gt;[i] is also HIGH, where x is 0 to 3. The configuration point MAINPPCEXP&lt;x&gt;DIS defines if each bit within this register is actually implemented such that if MAINPPCEXP&lt;x&gt;DIS[i] = 1&rsquo;b1 then MAINNSPPPCEXP&lt;x&gt;[i] is disabled and
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
