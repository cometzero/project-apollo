# System Control Peripheral Region

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region>

### System Control Peripheral Region

The System Control Peripheral Regions are a collection of memory regions where system control related peripherals are mapped. These peripherals reside either in the PD\_AON domain or in the PD\_MGMT domain if PILEVEL = 2. There are four regions in total as follows:

0x4002\_0000 to 0x4003\_FFFF
:   Non-secure region for low latency system control peripherals. Some peripherals may be expected to be aliased in its associated Secure region,
    0x5002\_0000 to
    0x5003\_FFFF.

0x4802\_0000 to 0x4803\_FFFF
:   Non-secure region for high latency system control peripherals. Some peripherals may be expected to be aliased in its associated Secure region,
    0x5802\_0000 to
    0x5803\_FFFF.

0x5002\_0000 to 0x5003\_FFFF
:   Secure region for low latency system control peripherals. Some peripherals may be expected to be aliased in its associated Non-secure region,
    0x4002\_0000 to
    0x4003\_FFFF.

0x5802\_0000 to 0x5803\_FFFF
:   Secure region for low latency system control peripherals. Some peripherals may be expected to be aliased in its associated Non-secure region,
    0x4802\_0000 to
    0x4803\_FFFF.

For an aliased peripheral in these regions, mapping of each peripheral to either Secure or Non-secure region is determined by Peripheral Protection Controllers (PPC) that are controlled using the Secure Access Configuration register block. These PPCs also define privileged or unprivileged accessibility. For more information, [Secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.").

The following table shows the System Control Peripheral Region address map.

The System Control Peripheral Region address map defines the following values for security:

NS\_PPC
:   Non-secure access only, gated by a PPC

S\_PPC
:   Secure access only, gated by a PPC

S
:   Secure access only

NS
:   Non-secure access only

P
:   Privileged access only

UP
:   Unprivileged and privileged access allowed

P\_PPC
:   Unprivileged access controlled by PPC

> ### Note
>
> When PPC protects a peripheral the configurability of the security or privileged attributes for a given peripheral is defined by [PERIPHSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC0?lang=en "Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:"), [PERIPHSPPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC1?lang=en "Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:"), [PERIPHNSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC0?lang=en "Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only Non-secure privileged access or is allowed Non-secure unprivileged access as well."), [PERIPHNSPPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC1?lang=en "Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Non-secure privileged access or is allowed Non-secure unprivileged access as well."), [PERIPHNSPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHNSPPC0?lang=en "The Peripheral Interconnect Non-secure Access Peripheral Protection Controller Registers allows software to configure if each peripheral on the Peripheral Interconnect that it controls through a PPC is Secure access only or is Non-secure access only."), and [PERIPHNSPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHNSPPC1?lang=en "The Peripheral Interconnect Non-secure Access Peripheral Protection Controller Registers allow software to configure if each peripheral on the Peripheral Interconnect that it controls through a PPC is Secure access only or is Non-secure access only.") registers.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   System Control Peripheral Region address map
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
   <th class="documents-nocellnorowborder" colspan="1" id="d54177e269" rowspan="1">
    <p>
     Row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d54177e273" rowspan="1">
    <p>
     From address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d54177e277" rowspan="1">
    <p>
     To address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d54177e281" rowspan="1">
    <p>
     Size
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d54177e285" rowspan="1">
    <p>
     Region name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d54177e290" rowspan="1">
    <p>
     Alias with row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d54177e294" rowspan="1">
    <p>
     Security
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d54177e298" rowspan="1">
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
      0x4002_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4003_FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     128KB
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
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4802_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4802_0FFF
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
     SYSINFO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS, UP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Information Register Block. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block?lang=en" title="The System Information Register Block provides information on the system configuration and identity. This register block is read-only and is accessible by accesses of any security attributes. This module resides at base address 5802_0000 in the Secure region, and 4802_0000 in the Non-secure region.">
      SYSINFO register block
     </a>
     .
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
      0x4802_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4802_EFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     56KB
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
     NS
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved. When accessed, results in
     <span class="documents-archterm">
      RAZ/WI
     </span>
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
      0x4802_F000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4802_FFFF
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
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     Timer
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     31
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer running on
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     . See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Timers-and-Watchdogs/SLOWCLK-AON-Timers?lang=en" href="/documentation/102803/0000/Functional-Description/Timers-and-Watchdogs/SLOWCLK-AON-Timers?lang=en" title="The second class of timers and watchdogs are simple CMSDK based 32-bit timers that run on SLOWCLK. They reside in PD_AON power domain and are reset by nWARMRESETAON. A single timer and a single Secure privileged Watchdog are provided and are expected to be used when the system is in HIBERNATION{0-1} when potentially only SLOWCLK is available and running and all other clocks are off.">
      SLOWCLK AON timers
     </a>
     .
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
      0x4803_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4803_FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     64KB
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
      0x5002_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5003_FFFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     128KB
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
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_0FFF
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
     SYSINFO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S, UP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Information Register Block. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block?lang=en" title="The System Information Register Block provides information on the system configuration and identity. This register block is read-only and is accessible by accesses of any security attributes. This module resides at base address 5802_0000 in the Secure region, and 4802_0000 in the Non-secure region.">
      SYSINFO register block
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
      0x5802_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_1FFF
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
     SYSCONTROL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     System Control Register Block. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block?lang=en" title="The System Control Register Block implements registers for power, clocks, resets, and other general system control. This module resides at base address 5802_1000 in the Secure region. The System Control Register Block is Secure privileged access only. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes results in its write data ignored.">
      System control register block
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     18
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_2FFF
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
     SYS_PPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_SYS. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
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
     <span class="documents-g.number.hex">
      0x5802_3000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_3FFF
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
     CPU0_PPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_CPU0. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     20
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_4FFF
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
     CPU1_PPU
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_CPU1. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     21
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_5000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_5FFF
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
     CPU2_PPU
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_CPU2. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     22
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_6000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_6FFF
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
     CPU3_PPU
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_CPU3. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     23
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_7000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_7FFF
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
     CRYPTO_PPU
     <sup>
      4
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_CRYPTO. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     24
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_8000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_8FFF
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
     MGMT_PPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_MGMT. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     25
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_9000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_9FFF
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
     DEBUG_PPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_DEBUG. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     26
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_A000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_AFFF
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
     NPU0_PPU
     <sup>
      5
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_NPU0. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
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
     <span class="documents-g.number.hex">
      0x5802_B000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_BFFF
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
     NPU1_PPU
     <sup>
      6
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_NPU1. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     28
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_C000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_CFFF
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
     NPU2_PPU
     <sup>
      7
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_NPU2. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     29
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_D000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_DFFF
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
     NPU3_PPU
     <sup>
      8
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PPU for BR_NPU3. See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Power-Policy-Units?lang=en" href="/documentation/102803/0000/Functional-Description/Power-Policy-Units?lang=en" title="CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm Power Policy Unit Architecture Specification and Arm CoreLink PCK-600 Power Control Kit Technical Reference Manual.">
      Power Policy Units
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     30
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_E000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_EFFF
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
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     Watchdog
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Watchdog Timer running on
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     . See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Timers-and-Watchdogs/SLOWCLK-AON-Timers?lang=en" href="/documentation/102803/0000/Functional-Description/Timers-and-Watchdogs/SLOWCLK-AON-Timers?lang=en" title="The second class of timers and watchdogs are simple CMSDK based 32-bit timers that run on SLOWCLK. They reside in PD_AON power domain and are reset by nWARMRESETAON. A single timer and a single Secure privileged Watchdog are provided and are expected to be used when the system is in HIBERNATION{0-1} when potentially only SLOWCLK is available and running and all other clocks are off.">
      SLOWCLK AON timers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     31
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_F000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5802_FFFF
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
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     Timer
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer running on
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SLOWCLK
      </span>
     </span>
     . See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Timers-and-Watchdogs/SLOWCLK-AON-Timers?lang=en" href="/documentation/102803/0000/Functional-Description/Timers-and-Watchdogs/SLOWCLK-AON-Timers?lang=en" title="The second class of timers and watchdogs are simple CMSDK based 32-bit timers that run on SLOWCLK. They reside in PD_AON power domain and are reset by nWARMRESETAON. A single timer and a single Secure privileged Watchdog are provided and are expected to be used when the system is in HIBERNATION{0-1} when potentially only SLOWCLK is available and running and all other clocks are off.">
      SLOWCLK AON timers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5803_0000
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5803_FFFF
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     64KB
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

1 When NUMCPU < 1, the CPU1\_PPU region is reserved and RAZ/WI.

2 When NUMCPU < 2, the CPU2\_PPU region is reserved and RAZ/WI.

3 When NUMCPU < 3, the CPU3\_PPU region is reserved and RAZ/WI.

4 When HASCRYPTO < 1, the CRYPTO\_PPU region is reserved and RAZ/WI.

5 When NUMNPU < 1, the NPU0\_PPU region is reserved and RAZ/WI.

6 When NUMNPU < 2, the NPU1\_PPU region is reserved and RAZ/WI.

7 When NUMNPU < 3, the NPU2\_PPU region is reserved and RAZ/WI.

8 When NUMNPU < 4, the NPU3\_PPU region is reserved and RAZ/WI.

- **[SYSINFO Register Block](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/SYSINFO-Register-Block?lang=en)**
   The System Information Register Block provides information on the system configuration and identity. This register block is read-only and is accessible by accesses of any security attributes. This module resides at base address 0x5802\_0000 in the Secure region, and 0x4802\_0000 in the Non-secure region.
- **[System Control Register Block](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block?lang=en)**
   The System Control Register Block implements registers for power, clocks, resets, and other general system control. This module resides at base address 0x5802\_1000 in the Secure region. The System Control Register Block is Secure privileged access only. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes results in its write data ignored.
