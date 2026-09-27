# CPUPWRCFG

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/CPU-Private-Region/CPU-n--PWRCTRL-register-block/CPUPWRCFG>

### CPUPWRCFG

The CPUPWRCFG register provides the local CPU software control registers for power control.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Type
:   This register is read only if accessed from the Non-secure region starting at address
    0x4001\_2000 and any write accesses to it in that region are ignored.

Power domain
:   This register resides in the same power domain, PD\_CPU<n>, as its associated CPU core so that when the CPU is powered down, the register is also powered down and is cleared when powered back up.

Reset
:   This register resides in the same reset domain,
    nWARMRESETCPU<n>, as its associated CPU core so that when the CPU is powered down, the register is also powered down and is cleared when powered back up.

### Usage constraints

Each CPU <n> can only see its own CPU<n>\_PWRCTRL registers.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CPUPWRCFG bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d123714e118" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d123714e122" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d123714e126" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d123714e130" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d123714e134" rowspan="1">
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
     31:5
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     TCM_MIN_PWR_STATE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Defines the minimum power state of the TCM for CPU&lt;n&gt;.
    </p>
    <ul>
     <li>
      <p>
       &lsquo;0&rsquo;: OFF,
      </p>
     </li>
     <li>
      <p>
       &lsquo;1&rsquo;: Retention.
      </p>
     </li>
    </ul>
    <p>
     This bit is read access only from the Non-secure world.
    </p>
    <p>
     When PD_CPU&lt;n&gt; returns from MEM_RET or MEM_RET_NOCACHE state to one of the ON states, this bit is set to 1&rsquo;b1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3:1
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
      0x0
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
     USEIWIC
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     When HIGH selects the use of IWIC for CPU &lt;n&gt; when in DeepSleep. Else selects the use of EWIC.
    </p>
    <p>
     If HASCPU&lt;n&gt;HASIWIC for this CPU &lt;n&gt; is 0, this field is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <p>
     This bit is read access only from the Non-secure world.
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
