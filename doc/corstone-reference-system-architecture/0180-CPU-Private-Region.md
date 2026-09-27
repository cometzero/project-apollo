# CPU Private Region

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/CPU-Private-Region>

### CPU Private Region

Each processor in the system has its own copy of the CPU Private Region which is only accessible to itself. Each CPU Private Region consists of four subregions as follows:

0x4001\_0000 to 0x4001\_FFFF
:   Implements a Non-secure Low Access Latency Region

0x4801\_0000 to 0x4801\_FFFF
:   Implements a Non-secure High Access Latency Region

0x5001\_0000 to 0x5001\_FFFF
:   Implements a Secure Low Access Latency Region

0x5801\_0000 to 0x5801\_FFFF
:   Implements a Secure High Access Latency Region

Each of these regions is not accessible from any other manager in the system, including from the expansion subordinate interfaces on the Main and Peripheral Interconnect, except through the external debugger through the local CPUs. Of the four preceding regions only 0x4001\_0000 to 0x4001\_FFFF and 0x5001\_0000 to 0x5001\_FFFF implements any registers.

The memory map of the CPU Private Region is detailed in the following table.

The CPU Private Region address map defines the following values for security:

S
:   Secure access only

NS
:   Non-secure access only

P
:   Privileged access only

UP
:   Unprivileged and privileged access allowed

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CPU Private Region address map
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d116735e173" rowspan="1">
    <p>
     Row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116735e177" rowspan="1">
    <p>
     From address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116735e181" rowspan="1">
    <p>
     To address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116735e185" rowspan="1">
    <p>
     Size
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116735e189" rowspan="1">
    <p>
     Region name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116735e194" rowspan="1">
    <p>
     Alias with row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116735e198" rowspan="1">
    <p>
     Security
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d116735e202" rowspan="1">
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
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4001_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4001_1FFF
     </span>
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
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
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
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4001_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4001_2FFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;_PWRCTRL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Power Control Block.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--PWRCTRL-register-block?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--PWRCTRL-register-block?lang=en" title="CRSAS Ma1 implements a CPU&lt;n&gt;_PWRCTRL register block for each CPU &lt;n&gt; in the subsystem. All blocks reside at address 4001_2000 in a Non-secure region and are also aliased to 5001_2000 in the Secure region. Each CPU &lt;n&gt; can only see its own CPU&lt;n&gt;_PWRCTRL registers. These are read-only registers when accessed from the Non-secure region starting at address 4001_2000 and any writes access to it in that region are ignored.">
      CPU&lt;n&gt;_PWRCTRL register block
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4001_3000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4001_EFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
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
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4001_F000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4001_FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;_IDENTITY
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     9
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS, UP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Identity Block.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--IDENTITY-register-block?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--IDENTITY-register-block?lang=en" title="CRSAS Ma1 implements a CPU&lt;n&gt;_IDENTITY register block for each CPU &lt;n&gt; in the subsystem. All blocks reside at address 4001_F000 in a Non-secure region and are also aliased to 5001_F000 in the Secure region. Each CPU &lt;n&gt; can only see its own CPU&lt;n&gt;_IDENTITY registers. These are read-only registers and any write accesses to the region are ignored.">
      CPU&lt;n&gt;_IDENTITY register block
     </a>
     .
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
     <span class="documents-g.number.hex">
      0x4801_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4801_FFFF
     </span>
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
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
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
     5
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_0FFF
     </span>
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
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
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
     6
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_1FFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;_SECCTRL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Local Security Control Block.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--SECCTRL-register-block?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--SECCTRL-register-block?lang=en" title="Each CPU &lt;n&gt; in the system has associated with it a CPU&lt;n&gt;_SECCTRL register block that allows the security locks of each CPU to be configured. Each register block resides in the same reset domain, nWARMRESETCPU&lt;n&gt;, and power domain as its associated CPU core so that when a CPU is powered down, they are also powered down and are cleared when powered back up. These registers are Secure access only and reside at address 5001_1000.">
      CPU&lt;n&gt;_SECCTRL register block
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_2FFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;_PWRCTRL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Power Control Block.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--PWRCTRL-register-block?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--PWRCTRL-register-block?lang=en" title="CRSAS Ma1 implements a CPU&lt;n&gt;_PWRCTRL register block for each CPU &lt;n&gt; in the subsystem. All blocks reside at address 4001_2000 in a Non-secure region and are also aliased to 5001_2000 in the Secure region. Each CPU &lt;n&gt; can only see its own CPU&lt;n&gt;_PWRCTRL registers. These are read-only registers when accessed from the Non-secure region starting at address 4001_2000 and any writes access to it in that region are ignored.">
      CPU&lt;n&gt;_PWRCTRL register block
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     8
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_3000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_EFFF
     </span>
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
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
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
     9
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_F000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5001_FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;_IDENTITY
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S, UP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Identity Block.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--IDENTITY-register-block?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--IDENTITY-register-block?lang=en" title="CRSAS Ma1 implements a CPU&lt;n&gt;_IDENTITY register block for each CPU &lt;n&gt; in the subsystem. All blocks reside at address 4001_F000 in a Non-secure region and are also aliased to 5001_F000 in the Secure region. Each CPU &lt;n&gt; can only see its own CPU&lt;n&gt;_IDENTITY registers. These are read-only registers and any write accesses to the region are ignored.">
      CPU&lt;n&gt;_IDENTITY register block
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     10
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5801_0000
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5801_FFFF
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
  </tr>
 </tbody>
</table>

- **[CPU<n>\_PWRCTRL register block](/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--PWRCTRL-register-block?lang=en)**
   CRSAS Ma1 implements a CPU<n>\_PWRCTRL register block for each CPU <n> in the subsystem. All blocks reside at address 0x4001\_2000 in a Non-secure region and are also aliased to 0x5001\_2000 in the Secure region. Each CPU <n> can only see its own CPU<n>\_PWRCTRL registers. These are read-only registers when accessed from the Non-secure region starting at address 0x4001\_2000 and any writes access to it in that region are ignored.
- **[CPU<n>\_IDENTITY register block](/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--IDENTITY-register-block?lang=en)**
   CRSAS Ma1 implements a CPU<n>\_IDENTITY register block for each CPU <n> in the subsystem. All blocks reside at address 0x4001\_F000 in a Non-secure region and are also aliased to 0x5001\_F000 in the Secure region. Each CPU <n> can only see its own CPU<n>\_IDENTITY registers. These are read-only registers and any write accesses to the region are ignored.
- **[CPU<n>\_SECCTRL register block](/documentation/102803/0000/Programmers-model/CPU-Private-Region/CPU-n--SECCTRL-register-block?lang=en)**
   Each CPU <n> in the system has associated with it a CPU<n>\_SECCTRL register block that allows the security locks of each CPU to be configured. Each register block resides in the same reset domain, nWARMRESETCPU<n>, and power domain as its associated CPU core so that when a CPU is powered down, they are also powered down and are cleared when powered back up. These registers are Secure access only and reside at address 0x5001\_1000.
