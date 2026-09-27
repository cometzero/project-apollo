# SYS_CONFIG2

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block/SYS-CONFIG2>

### SYS\_CONFIG2

The System Hardware Configuration Registers provide several registers to allow software to find out about the configuration of the CRSAS Ma1 based subsystem. See also [SYS\_CONFIG0](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block/SYS-CONFIG0?lang=en "The System Hardware Configuration Registers provide several registers that allow software to query the configuration of the CRSAS Ma1 based subsystem. See also SYS_CONFIG1 and SYS_CONFIG2.") and [SYS\_CONFIG1](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block/SYS-CONFIG1?lang=en "The System Hardware Configuration Registers provide several registers to allow software to find out about the configuration of the CRSAS Ma1 based subsystem. See also SYS_CONFIG0 and SYS_CONFIG2.").

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
   SYS_CONFIG2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d6385e126" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d6385e130" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d6385e134" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d6385e138" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d6385e142" rowspan="1">
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
     31:15
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     14:12
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DMA_TYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DMA Core Type:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;000&rsquo;: Does not exist
      </p>
     </li>
     <li>
      <p>
       &lsquo;001&rsquo;: DMA-350
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
     DMATYPE
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11:9
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU3_TYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU 3 Core Type:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;000&rsquo;: Does not exist
      </p>
     </li>
     <li>
      <p>
       &lsquo;001&rsquo;: Ethos-U55
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
     NPU3TYPE
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     8:6
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU2_TYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU 2 Core Type:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;000&rsquo;: Does not exist
      </p>
     </li>
     <li>
      <p>
       &lsquo;001&rsquo;: Ethos-U55
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
     NPU2TYPE
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     5:3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU1_TYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU 1 Core Type:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;000&rsquo;: Does not exist
      </p>
     </li>
     <li>
      <p>
       &lsquo;001&rsquo;: Ethos-U55
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
     NPU1TYPE
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     2:0
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     NPU0_TYPE
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     NPU 0 Core Type:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;000&rsquo;: Does not exist
      </p>
     </li>
     <li>
      <p>
       &lsquo;001&rsquo;: Ethos-U55
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     NPU0TYPE
    </p>
   </td>
  </tr>
 </tbody>
</table>
