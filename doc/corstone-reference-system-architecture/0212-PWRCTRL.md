# PWRCTRL

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PWRCTRL>

### PWRCTRL

The Power Control register configures the power control features in CRSAS Ma1 System.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32-bit

Power domain
:   This register resides in the PD\_AON power domain but can also reside in PD\_MGMT power domain when PILEVEL = 2 if its states are saved and restored when entering and then leaving the lower power state, respectively.

Reset
:   This register is reset by
    nWARMRESETAON.

### Usage constraints

This register is Secure privileged access only. For write access to this register, only 32-bit writes are supported. Any byte and halfword writes are ignored.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PWRCTRL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d98454e107" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d98454e111" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d98454e115" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d98454e119" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d98454e123" rowspan="1">
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
     31:2
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
      0x0000_0000
     </span>
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
     PPU_ACCESS_UNLOCK
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PPU_ACCESS_FILTER write unlock. When &lsquo;1&rsquo;, noth PPU_ACCESS_FILTER and this register bits can be written. When set to &lsquo;0&rsquo;, the PPU_ACCESS_FILTER and this register bit is no longer writable, and PPU_ACCESS_UNLOCK stays &lsquo;0&rsquo;.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW0C
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x01
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
     PPU_ACCESS_FILTER
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Filter Access to PPU Registers. When set to &lsquo;1&rsquo;, only key PPU interrupt handling registers are open to write access, and all other PPU registers are read only. When set to &lsquo;0&rsquo;, it releases all PPU registers to full access. For more information in PPU registers accessibility, see
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
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
      0x01
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
