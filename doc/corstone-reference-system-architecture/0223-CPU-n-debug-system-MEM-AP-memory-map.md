# CPU<n> debug system MEM-AP memory map

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented/CPU-n--debug-system-MEM-AP-memory-map>

### CPU<n> debug system MEM-AP memory map

The CPU<n> Debug System Memory Access Port provides access to the following;

- CPU<n> Debug CoreSight ROM Table, which the CPU<n> MEM-AP’s base address static configuration is configured to point to. This ROM Table includes Granular Power Requester (GPR) functionality to allow software to wake CPU<n>.
- CPU’s Debug access interface, which provides access to the processor control and debug logic, and to a view of memory which is consistent with that observed by CPU<n>. This includes the CPU’s PPB region, where other CPU<n> private debug components can be hosted. For more information, see [CPU Private Peripheral Bus region](/documentation/102803/0000/Programmers-model/CPU-Private-Peripheral-Bus-region?lang=en "Each CPU, as defined by the ARMv8-M architecture specification, hosts a local Private Peripheral Bus Region (PPB) at address E000_0000 to E00F_FFFF. This region is typically for integration with CoreSight debug and trace components that is normally local to each CPU and is not intended for general peripheral usage.") and Arm® Cortex®-M55 Processor Technical Reference Manual and Arm® Cortex®-M85 Processor Technical Reference Manual.

The following table shows the memory map of the memory map as seen by the CPU<n> MEM-AP.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CPU&lt;n&gt; MEM-AP memory map
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
   <th class="documents-nocellnorowborder" colspan="1" id="d126069e110" rowspan="1">
    <p>
     Row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126069e114" rowspan="1">
    <p>
     From address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126069e118" rowspan="1">
    <p>
     To address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126069e122" rowspan="1">
    <p>
     Size
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d126069e126" rowspan="1">
    <p>
     Region name
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d126069e131" rowspan="1">
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
     1
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
     <span class="documents-g.number.hex">
      0xF000_7FFF
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
     SYSACC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Memory Access through CPU&lt;n&gt; Debug Access Interface.
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
      0xF000_8000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF000_8FFF
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
     CPU&lt;n&gt;ROM
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt; Debug ROM Table.
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
      0xF000_9000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0000_9FFF
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
     Reserved
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF000_A000
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFFFF_FFFF
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
     SYSACC
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     System Memory Access through CPU&lt;n&gt; Debug Access Interface.
    </p>
   </td>
  </tr>
 </tbody>
</table>
