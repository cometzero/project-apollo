# SYS_CONFIG0

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block/SYS-CONFIG0>

### SYS\_CONFIG0

The System Hardware Configuration Registers provide several registers that allow software to query the configuration of the CRSAS Ma1 based subsystem. See also [SYS\_CONFIG1](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block/SYS-CONFIG1?lang=en "The System Hardware Configuration Registers provide several registers to allow software to find out about the configuration of the CRSAS Ma1 based subsystem. See also SYS_CONFIG0 and SYS_CONFIG2.") and [SYS\_CONFIG2](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block/SYS-CONFIG2?lang=en "The System Hardware Configuration Registers provide several registers to allow software to find out about the configuration of the CRSAS Ma1 based subsystem. See also SYS_CONFIG0 and SYS_CONFIG1.").

In the following table, the fields CPU<n>\_TCM\_BANK\_NUM and CPU<n>\_HAS\_SYSTCM refer to TCMs that are implemented on the system interconnect close to each associated CPU, rather than the TCMs that are implemented within the CPU core. CRSAS Ma1 currently does not support TCMs being implemented on the system interconnect and hence these fields are reserved and RAZ/WI.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Type
:   This register is read-only and is accessible by accesses of any security attributes.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SYS_CONFIG0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d37130e138" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d37130e142" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d37130e146" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d37130e150" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d37130e154" rowspan="1">
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
     31:28
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU1_TCM_BANK_NUM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The VM Bank that is the TCM memory for CPU 1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     27
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU1_HAS_SYSTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 1 has System TCM:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;0&rsquo;: No
      </p>
     </li>
     <li>
      <p>
       &lsquo;1&rsquo;: Yes
      </p>
     </li>
    </ul>
    <p>
     This is not the CPU&rsquo;s local ITCM or DTCM, but instead these are the TCMs that are implemented at system level.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     26:24
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU1_TYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 1 Core Type:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;000&rsquo;: Does not exist
      </p>
     </li>
     <li>
      <p>
       &lsquo;011&rsquo;: Cortex-M55 Processor
      </p>
     </li>
     <li>
      <p>
       &lsquo;100&rsquo;: Cortex-M85
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU1TYPE
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     23:20
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU0_TCM_BANK_NUM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The VM Bank that is the TCM memory for CPU 0.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     19
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU0_HAS_SYSTCM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 0 has System TCM:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;0&rsquo; = No
      </p>
     </li>
     <li>
      <p>
       &lsquo;1&rsquo; = Yes.
      </p>
     </li>
    </ul>
    <p>
     This is not the CPU&rsquo;s local ITCM or DTCM, but instead these are the TCMs that are implemented at system level.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     18:16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU0_TYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU 0 Core Type:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;000&rsquo;: Does not exist
      </p>
     </li>
     <li>
      <p>
       &lsquo;011&rsquo;: Cortex-M55 Processor
      </p>
     </li>
     <li>
      <p>
       &lsquo;100&rsquo;: Cortex-M85
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU0TYPE
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15:13
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
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
     12:11
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PI_LEVEL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Power Infrastructure Level:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;00&rsquo;: Basic Level
      </p>
     </li>
     <li>
      <p>
       &lsquo;01&rsquo;: Intermediate Level
      </p>
     </li>
     <li>
      <p>
       &lsquo;10&rsquo;: Advanced Level
      </p>
     </li>
     <li>
      <p>
       Others: Reserved.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PILEVEL
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     10
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     HAS_CSS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Includes CoreSight SoC-600 based Debug infrastructure.
    </p>
    <ul>
     <li>
      <p>
       &lsquo;0&rsquo;: No
      </p>
     </li>
     <li>
      <p>
       &lsquo;1&rsquo;: Yes
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     HASCSS
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
     HAS_CRYPTO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Includes CryptoCell:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;0&rsquo;: No
      </p>
     </li>
     <li>
      <p>
       &lsquo;1&rsquo;: Yes
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     HASCRYPTO
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     8:4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     VM_ADDR_WIDTH
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Volatile Memory Bank Address Width, where the size of each bank is equal to 2
     <sup>
      VM_ADDR_WIDTH
     </sup>
     bytes.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     VMADDRWIDTH
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
     NUM_VM_BANK
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of Volatile Memory Banks.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     NUMVMBANK
    </p>
   </td>
  </tr>
 </tbody>
</table>
