# CoreSight SoC-600 based Debug System implemented

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented>

###

When the CoreSight based System Debug infrastructure exists within an implementation of CRSAS Ma1 (HASCSS=1), the system provides several Memory Access Ports (MEM-APs) to provide access to each CPU and to the shared debug components in the system.

These ports are mapped to the Debug system region with a relative address map as shown in the following table.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Debug system address map
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
   <th class="documents-nocellnorowborder" colspan="1" id="d125109e70" rowspan="1">
    <p>
     Row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d125109e74" rowspan="1">
    <p>
     From address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d125109e78" rowspan="1">
    <p>
     To adress
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d125109e82" rowspan="1">
    <p>
     Size
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d125109e86" rowspan="1">
    <p>
     Region name
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d125109e91" rowspan="1">
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
      0x0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0FFF
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
     DSROM
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Debug System ROM.
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
      0x1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1FFF
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x3FFF
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
     SYS APB-AP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Shared Debug System Access Port.
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
      0x4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5FFF
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
     CPU0 AHB-AP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU 0 Debug System Access Port.
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
      0x6000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x7FFF
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
     CPU1 AHB-AP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU 1 Debug System Access Port.
    </p>
    <p>
     This AP does not exist when NUMCPU &lt; 1, and the region is reserved.
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
      0x8000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x9FFF
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
     CPU2 AHB-AP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU 2 Debug System Access Port.
    </p>
    <p>
     This AP does not exist when NUMCPU &lt; 2, and the region is reserved.
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
      0xA000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xBFFF
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
     CPU3 AHB-AP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU 3 Debug System Access Port.
    </p>
    <p>
     This AP does not exist when NUMCPU &lt; 3, and the region is reserved.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     8
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xC000
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF_FFFF
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Reserved
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

This region is accessible through:

- The Debug Access Interface with an address offset of 0x0000. Access is first controlled using the Debug Authentication Access Control signal DAPDSSACCEN. When DAPDSSACCEN = 0, accesses from the Debug Access Interface are blocked and return error responses. If DAPDSSACCEN = 1, accesses are allowed to pass through. Note that a separate DAPACCEN is provided to allow the integrator to control a DAP interface directly to stop access even reaching the Debug Access Interface in the first place. This allows debug components outside the subsystem, with DAPACCEN = 1, to still be accessible while DAPDSSACCEN = 0 stops accesses arriving at the subsystem Debug Access Interface from accessing the system.
- The Main and Peripheral Interconnect are at the following two aliased address offsets:

  - 0xE010\_0000 is the Non-secure alias
  - 0xF010\_0000 is the Secure alias

  Access from the interconnect is gated by the Debug Authentication Access Control signal, SYSDSSACCEN<n>. When SYSDSSACCEN<n> = 0, accesses from CPU <n> through the Main Interconnect are blocked and return error responses. If SYSDSSACCEN<n> = 1, accesses from CPU <n> are allowed to pass through.

  Once access can pass the first gate controlled by SYSDSSACCEN<n> into the Debug System, a PPC0 is then used to perform the final mapping of all APs either to the Non-secure region from 0xE010\_0000 to 0xE01F\_FFFF or to the Secure region from 0xF010\_0000 to 0xF01F\_FFFF. For more information, see [PERIPHNSPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHNSPPC0?lang=en "The Peripheral Interconnect Non-secure Access Peripheral Protection Controller Registers allows software to configure if each peripheral on the Peripheral Interconnect that it controls through a PPC is Secure access only or is Non-secure access only."), [PERIPHNSPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHNSPPC1?lang=en "The Peripheral Interconnect Non-secure Access Peripheral Protection Controller Registers allow software to configure if each peripheral on the Peripheral Interconnect that it controls through a PPC is Secure access only or is Non-secure access only."), [PERIPHSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC0?lang=en "Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:"), [PERIPHSPPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC1?lang=en "Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:"), [PERIPHNSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC0?lang=en "Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only Non-secure privileged access or is allowed Non-secure unprivileged access as well."), and [PERIPHNSPPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC1?lang=en "Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Non-secure privileged access or is allowed Non-secure unprivileged access as well.").
- Each Memory Access Port (MEM-AP) is a twin MEM-AP that enables an external debugger to use one logical MEM-AP, and on-chip software to use a separate logical MEM-AP. A twin MEM-AP consists of two sets of 4K registers. The bottom 4K is for the external debugger accesses exclusively while the top 4K is for on-chip software accesses exclusively. It is IMPLEMENTATION DEFINED if the external debugger only has access to the top 4K and vice versa if the on-chip software only has access to the bottom 4K.

The following sections list the memory map behind each MEM-AP and the contents of CoreSight Debug ROMs.

- **[Shared debug system MEM-AP memory map](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented/Shared-debug-system-MEM-AP-memory-map?lang=en)**
   The Shared debug system MEM-AP provides access to the Shared debug system that all CPUs in the system shares. It includes a trace funnel for funneling all trace data together, an Embedded Trace Buffer (ETB) that allows trace data to be stored and read by a debugger. In addition, it provides access to debug components that reside in the expansion system through the Debug APB Expansion Interface.
- **[CPU<n> debug system MEM-AP memory map](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented/CPU-n--debug-system-MEM-AP-memory-map?lang=en)**
   The CPU<n> Debug System Memory Access Port provides access to the following;
- **[DSROM, Debug System ROM](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented/DSROM--Debug-System-ROM?lang=en)**
   The Debug System ROM is a CoreSight Class 0x1 ROM table that provides a list of pointers to Access Port within the Debug System.
- **[SDSROM, Shared Debug System ROM](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented/SDSROM--Shared-Debug-System-ROM?lang=en)**
   The Shared Debug System Debug CoreSight ROM is a CoreSight Class 0x1 ROM table that provides a list of pointers to the following:
- **[CPU<n>ROM, CPU<n> Debug System ROM](/documentation/102803/0000/Programmers-model/Debug-System-Access-Region/CoreSight-SoC-600-based-Debug-System-implemented/CPU-n-ROM--CPU-n--Debug-System-ROM?lang=en)**
   The CPU<n> Debug System ROM is a CoreSight Class 0x9 ROM table that provides a list of pointers to the following:
