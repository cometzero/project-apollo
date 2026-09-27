# CPU<n>_SECCTRL register block

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/CPU-Private-Region/CPU-n--SECCTRL-register-block>

### CPU<n>\_SECCTRL register block

Each CPU <n> in the system has associated with it a CPU<n>\_SECCTRL register block that allows the security locks of each CPU to be configured. Each register block resides in the same reset domain, nWARMRESETCPU<n>, and power domain as its associated CPU core so that when a CPU is powered down, they are also powered down and are cleared when powered back up. These registers are Secure access only and reside at address 0x5001\_1000.

The following table lists the registers in each CPU<n>\_SECCTRL Register block.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CPU&lt;n&gt;_SECCTRL Register Map
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d126833e76" rowspan="1">
    <p>
     Offset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126833e80" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126833e84" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126833e88" rowspan="1">
    <p>
     Reset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126833e92" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d126833e97" rowspan="1">
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
     <span class="documents-g.number.hex">
      0x000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPUSECCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Local Security Configuration. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--SECCTRL-register-block/CPUSECCFG?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--SECCTRL-register-block/CPUSECCFG?lang=en" title="The CPU Local Security Configuration Register allows software to set security lock bits at the interface of each associated CPU&lt;n&gt;.">
      CPUSECCFG
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x004
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0xFCC
     </span>
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFD0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0004
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 4
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFD4
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0xFDC
     </span>
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0059
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 0
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00B8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 1
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFE8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_001B
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 2
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFEC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PIDR3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Peripheral ID 3
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CIDR0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_000D
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID 0
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF4
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CIDR1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00F0
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID 1
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFF8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CIDR2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_0005
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Component ID 2
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFFC
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CIDR3
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_00B1
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Component ID 3
    </p>
   </td>
  </tr>
 </tbody>
</table>

- **[CPUSECCFG](/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--SECCTRL-register-block/CPUSECCFG?lang=en)**
   The CPU Local Security Configuration Register allows software to set security lock bits at the interface of each associated CPU<n>.
