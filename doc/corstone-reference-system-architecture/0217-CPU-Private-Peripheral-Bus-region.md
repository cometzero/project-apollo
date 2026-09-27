# CPU Private Peripheral Bus region

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/CPU-Private-Peripheral-Bus-region>

### CPU Private Peripheral Bus region

Each CPU, as defined by the ARMv8-M architecture specification, hosts a local Private Peripheral Bus Region (PPB) at address 0xE000\_0000 to 0xE00F\_FFFF. This region is typically for integration with CoreSight debug and trace components that is normally local to each CPU and is not intended for general peripheral usage.

In CRSAS Ma1, this region has the memory map as shown in the table below. Other than the EWIC, CPU <n> ROM Table, and the peripherals on the External PPB Expansion that is added by an integrator, the existence of all other components depends on the CPU implementation and configuration. See Arm® Cortex®-M55 Processor Technical Reference Manual and Arm® Cortex®-M85 Processor Technical Reference Manual.

Not included in the table are TPIU and the ETB, along with a system level debug CoreSight ROM table. This ROM table is also referred to as MCU ROM Table in CPU Technical Reference Manual. Depending on HASCSS:

- If HASCSS = 0 where NUMCPU must be 0, the TPIU, ETB, and the MCU ROM can be integrated using the CPU<n> EPPB Interface, with the MCU ROM pointing to the TPIU, ETB, and the core’s internal ROM table. We recommend that in this case, these are integrated at the following addresses:

  - TPIU at 0xE004\_0000
  - ETB at 0xE004\_5000
  - MCU ROM table at 0xE00F\_E000 where an external DAP-Lite or AHB-AP point to.
- If HASCSS = 1, the TPIU and the ETB are be provided

CRSAS Ma1 in the Shared Debug System accessible through a separate MEM-AP. The MCU ROM table can still be added to the EPPB if other debug related components local to the CPU exist so that the MCU ROM table can point to them. Note however that in such a system, the MCU ROM table does not point to the core’s internal ROM. Instead, the CPU<n> ROM table provided points to the core’s internal ROM. We recommend that the MCU ROM table, if it exists is integrated at 0xE00F\_E000.

When HASCSS = 1, Arm does not recommend using this region to expand the debug system, unless the intention is to implement independent debug infrastructure for each CPU. Instead the system integrator should add to the Debug APB Expansion Interface.

For more information on the ETM, CTI, PMC, SBIST and ROM Table, see Arm® Cortex®-M55 Processor Technical Reference Manual and Arm® Cortex®-M85 Processor Technical Reference Manual.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CPU &lt;n&gt; Private Peripheral Bus Region
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
   <th class="documents-nocellnorowborder" colspan="1" id="d15400e157" rowspan="1">
    <p>
     Row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d15400e161" rowspan="1">
    <p>
     From address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d15400e165" rowspan="1">
    <p>
     To address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d15400e169" rowspan="1">
    <p>
     Size
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d15400e173" rowspan="1">
    <p>
     Region name
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d15400e178" rowspan="1">
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
      0xE004_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_0FFF
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
     PPB Expansion
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Expansion PPB Interface.
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
      0xE004_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_1FFF
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
     ETM
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Embedded Trace Module.
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
      0xE004_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_2FFF
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
     CTI
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Cross Trigger Interface.
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
      0xE004_3000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_4FFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     8KB
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     5
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_5000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_5FFF
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
     PPB Expansion
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Expansion PPB Interface.
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
      0xE004_6000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_6FFF
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
     PMC
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Programmable MBIST Controller.
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
      0xE004_7000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_7FFF
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
     EWIC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     External Wakeup Interrupt Controller. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/CPU-Private-Peripheral-Bus-region/EWIC?lang=en" href="/documentation/102803/0000/Programmers-model/CPU-Private-Peripheral-Bus-region/EWIC?lang=en" title="CRSAS Ma1 is designed to always support an External Wakeup Interrupt Controller (EWIC) for each CPU in the system. This allows the system to support each CPU being switched off independently, and for the EWIC to run at a lower clock rate to help reduce PD_AON dynamic and leakage power consumption.">
      EWIC
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
      0xE004_8000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE004_8FFF
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
     PPB Expansion
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved for SBIST - Software Based Build In Self Test. Routed to CPU&lt;n&gt; Expansion PPB Interface on PD_CPU&lt;n&gt; power domain.
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
      0xE004_9000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE00F_EFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     24KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PPB Expansion
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Expansion PPB Interface.
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
      0xE00F_F000
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE00F_FFFF
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     4KB
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     ROM Table
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     CPU &lt;n&gt; Internal ROM Table.
    </p>
   </td>
  </tr>
 </tbody>
</table>

1 The existence of the following components is dependent of the configuration and the supported features of the CPU integrated. If they do not exist, these regions are reserved and RAZ/WI response when accessed.

- ETM
- CTI
- PMC

- **[EWIC](/documentation/102803/0000/Programmers-model/CPU-Private-Peripheral-Bus-region/EWIC?lang=en)**
   CRSAS Ma1 is designed to always support an External Wakeup Interrupt Controller (EWIC) for each CPU in the system. This allows the system to support each CPU being switched off independently, and for the EWIC to run at a lower clock rate to help reduce PD\_AON dynamic and leakage power consumption.
