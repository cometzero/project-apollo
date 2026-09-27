# CPUID

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/CPU-Private-Region/CPU-n--IDENTITY-register-block/CPUID>

### CPUID

The CPUID Register is a read only register that, when read by CPU <n>, provides an identity code to the CPU that is unique to that CPU.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Type
:   This register is read only and any write accesses to it are ignored.

Power domain
:   This register resides in the same power domain, PD\_CPU<n>, as its associated CPU core so that when the CPU is powered down, the register is also powered down and is cleared when powered back up.

Reset
:   This register resides in the same reset domain,
    nWARMRESETCPU<n>, as its associated CPU core so that when the CPU is powered down, the register is also powered down and is cleared when powered back up.

### Usage constraints

Each CPU <n> can only see its own CPU<n>\_IDENTITY registers.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CPUID bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d25097e115" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25097e119" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25097e123" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25097e127" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d25097e131" rowspan="1">
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
     31:4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
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
      0x000_0000
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CPUID
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CPU Identity. Defined by configuration CPU&lt;n&gt;CPUIDRST.
    </p>
    <p>
     The identity value for each CPU &lt;n&gt; must be unique.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;CPUIDRST
    </p>
   </td>
  </tr>
 </tbody>
</table>
