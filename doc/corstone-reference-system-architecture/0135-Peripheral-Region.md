# Peripheral Region

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/Peripheral-Region>

### Peripheral Region

The Peripheral Region are memory regions where the peripherals of the system reside. There are eight regions in total:

0x4000\_0000 to 0x4000\_FFFF
:   Non-secure region for low latency peripherals that are expected to be aliased in its associated Secure region,
    0x5000\_0000 to
    0x5000\_FFFF.

0x4004\_0000 to 0x400F\_FFFF
:   Non-secure region for low latency peripherals that are expected to be not aliased.

0x4800\_0000 to 0x4800\_FFFF
:   Non-secure region for high latency peripherals that are expected to be aliased in its associated Secure region,
    0x5800\_0000 to
    0x5800\_FFFF.

0x4804\_0000 to 0x480F\_FFFF
:   Non-secure region for high latency peripherals that are expected to be not aliased.

0x5000\_0000 to 0x5000\_FFFF
:   Secure region for low latency peripherals that are expected to be aliased in its associated Non-secure region,
    0x4000\_0000 to
    0x4000\_FFFF.

0x5004\_0000 to 0x500F\_FFFF
:   Secure region for low latency peripherals that are expected to be not aliased.

0x5800\_0000 to 0x5800\_FFFF
:   Secure region for high latency peripherals that are expected to be aliased in its associated Non-secure region,
    0x4800\_0000 to
    0x4800\_FFFF.

0x5804\_0000 to 0x580F\_FFFF
:   Secure region for high latency peripherals that are expected to be not aliased.

For regions that are aliased to both a Secure and a Non-secure region, the final mapping of a peripheral in these regions to either a Secure or a Non-secure region is either determined by Peripheral Protection Controller (PPC) that is programmed using Secure Access Configuration registers, or determined by the peripheral that intrinsically supports TrustZone.

The following table shows the memory map of the Peripheral Regions.

The Peripheral Region address map defines the following values for security:

NS\_PPC
:   Non-secure access only, gated by a PPC.

S\_PPC
:   Secure access only, gated by a PPC.

S
:   Secure access only.

NS
:   Non-secure access only.

P
:   Privileged access only

UP
:   Unprivileged and privileged access allowed

P\_PPC
:   Unprivileged access controlled by PPC

When PPC protects a peripheral, the configurability of the security or privileged attributes for a given peripheral is defined by [PERIPHSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC0?lang=en "Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:"), [PERIPHSPPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC1?lang=en "Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:"), [PERIPHNSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC0?lang=en "Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only Non-secure privileged access or is allowed Non-secure unprivileged access as well."), [PERIPHNSPPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC1?lang=en "Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Non-secure privileged access or is allowed Non-secure unprivileged access as well."), [NPUSPPORSL](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/NPUSPPORSL?lang=en "The NPU Secure Access Security Level Reset Control Register allows software to configure if each NPU resets to Secure or Non-secure state. The value of this register is only sampled by the NPU, when the NPU is released from reset. The default reset value of this register is controlled by NPU<m>PORSLRST."), [NPUNSPORPL](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/NPUNSPORPL?lang=en "The NPU power on reset Non-secure access privileged level reset control registers allow software to configure if each NPU resets to privileged or unprivileged state."), [NPUSPPORPL](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/NPUSPPORPL?lang=en "The NPU Secure Access Privileged Level Reset Control Register allows software to configure if each NPU resets to privileged or unprivileged state. The value of this register is only sampled by the NPU, when the NPU is released from reset and NPUSPPORSL.SP_NPU<m>PORSL is Secure State. The default reset value of this register is controlled by NPU<m>PORPLRST:"), [PERIPHNSPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHNSPPC0?lang=en "The Peripheral Interconnect Non-secure Access Peripheral Protection Controller Registers allows software to configure if each peripheral on the Peripheral Interconnect that it controls through a PPC is Secure access only or is Non-secure access only."), and [PERIPHNSPPC1](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHNSPPC1?lang=en "The Peripheral Interconnect Non-secure Access Peripheral Protection Controller Registers allow software to configure if each peripheral on the Peripheral Interconnect that it controls through a PPC is Secure access only or is Non-secure access only.") registers.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Peripheral Region address map
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
   <th class="documents-nocellnorowborder" colspan="1" id="d67281e332" rowspan="1">
    <p>
     Row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67281e336" rowspan="1">
    <p>
     From address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67281e340" rowspan="1">
    <p>
     To address
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67281e344" rowspan="1">
    <p>
     Size
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67281e348" rowspan="1">
    <p>
     Region name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67281e353" rowspan="1">
    <p>
     Alias with row ID
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d67281e357" rowspan="1">
    <p>
     Security
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d67281e361" rowspan="1">
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
      0x4000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4000_0FFF
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
     MHU0
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     23
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Message Handling Unit 0.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Message-Handling-Unit?lang=en" href="/documentation/102803/0000/Functional-Description/Message-Handling-Unit?lang=en" title="When NUMCPU &gt; 0, CRSAS Ma1 implements two Message Handling Units (MHUs) to allow processors to interrupt each other to pass message. Two MHUs are provided so that it is possible for software to place one MHU in the Secure world and another in the Non-secure world. Both MHUs reside in the PD_SYS power domain and are reset using the nWARMRESETSYS.">
      Message Handling Unit
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
      0x4000_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4000_1FFF
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
     MHU1
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     24
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Message Handling Unit 1.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Message-Handling-Unit?lang=en" href="/documentation/102803/0000/Functional-Description/Message-Handling-Unit?lang=en" title="When NUMCPU &gt; 0, CRSAS Ma1 implements two Message Handling Units (MHUs) to allow processors to interrupt each other to pass message. Two MHUs are provided so that it is possible for software to place one MHU in the Secure world and another in the Non-secure world. Both MHUs reside in the PD_SYS power domain and are reset using the nWARMRESETSYS.">
      Message Handling Unit
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
      0x4000_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4000_3FFF
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
     DMA
     <sup>
      4
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     25
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS, UP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     DMA Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/DMA-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/DMA-registers?lang=en" title="CRSAS Ma1 implements up to one DMA-350. See Arm CoreLink DMA-350 Controller Technical Reference Manual for full details of the DMA software interface. Security and privilege checking of accesses to DMA registers are handled by the DMA.">
      DMA registers
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
      0x4000_4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4000_4FFF
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
     NPU0
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     26
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU0 Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" title="CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm Ethos-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.">
      NPU&lt;m&gt; registers
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
      0x4000_5000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4000_5FFF
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
     NPU1
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     27
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU1 Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" title="CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm Ethos-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.">
      NPU&lt;m&gt; registers
     </a>
     .
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
      0x4000_6000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4000_6FFF
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
     NPU2
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     28
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU2 Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" title="CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm Ethos-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.">
      NPU&lt;m&gt; registers
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
      0x4000_7000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4000_7FFF
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
     NPU3
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     29
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU3 Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" title="CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm Ethos-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.">
      NPU&lt;m&gt; registers
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
      0x4000_8000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4000_FFFF
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
     Reserved. (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
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
      0x4004_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4007_FFFF
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
     10
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4008_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4008_0FFF
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
     NSACFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Non-secure Access Configuration Register Block.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block?lang=en" title="The Non-secure Access Configuration Register Block implements program visible states that allow software to control various security gating units within the design. This register block base address is 4008_0000. These registers are Non-secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.">
      Non-secure access configuration register block
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4008_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4008_FFFF
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
     Reserved (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     12
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4009_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4009_3FFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CryptoCell312
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS, UP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CryptoCell 312.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en" href="/documentation/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en" title="When HASCRYPTO = 1, CryptoCell-312 exists in the system and therefore, any interfaces and configuration that are associated with CryptoCell-312 also exist.">
      Has-Crypto configuration
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     13
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4009_4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x400F_FFFF
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
     14
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_0FFF
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
     TIMER0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     41
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer 0.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" title="CRSAS Ma1 implements four timestamp-based timers in the system, TIMER&lt;x&gt; where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.">
      Timestamp-based timers registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_1FFF
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
     TIMER1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     42
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer 1.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" title="CRSAS Ma1 implements four timestamp-based timers in the system, TIMER&lt;x&gt; where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.">
      Timestamp-based timers registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_2FFF
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
     TIMER2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     43
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer 2.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" title="CRSAS Ma1 implements four timestamp-based timers in the system, TIMER&lt;x&gt; where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.">
      Timestamp-based timers registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     17
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_3000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_3FFF
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
     TIMER3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     44
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer 3.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" title="CRSAS Ma1 implements four timestamp-based timers in the system, TIMER&lt;x&gt; where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.">
      Timestamp-based timers registers
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
      0x4800_4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4800_FFFF
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
     Reserved (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
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
      0x4804_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4804_0FFF
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
     NSWDCTRL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Non-secure Watchdog Control Frame. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en" title="CRSAS Ma1 implements two timestamp-based watchdogs in the system. All reside in the PD_SYS power domain and are reset by nWARMRESETSYS. One watchdog timer is Secure access only, while another is Non-secure. Each Watchdog Timer implements two register frames, a Control Frame and a Refresh Frame. The Control Frame is always fixed privileged while the Refresh Frame accessibility to unprivileged access is configurable and controlled by PPC0. See PERIPHSPPPC0 and PERIPHNSPPPC0.">
      Timestamp-based Watchdogs registers
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
      0x4804_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4804_1FFF
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
     NSWDREF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NS_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Non-secure Watchdog Refresh Frame. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en" title="CRSAS Ma1 implements two timestamp-based watchdogs in the system. All reside in the PD_SYS power domain and are reset by nWARMRESETSYS. One watchdog timer is Secure access only, while another is Non-secure. Each Watchdog Timer implements two register frames, a Control Frame and a Refresh Frame. The Control Frame is always fixed privileged while the Refresh Frame accessibility to unprivileged access is configurable and controlled by PPC0. See PERIPHSPPPC0 and PERIPHNSPPPC0.">
      Timestamp-based Watchdogs registers
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
      0x4804_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4804_FFFF
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
     Reserved (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
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
      0x4805_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x480F_FFFF
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
     23
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_0FFF
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
     MHU0
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Message Handling Unit 0.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Message-Handling-Unit?lang=en" href="/documentation/102803/0000/Functional-Description/Message-Handling-Unit?lang=en" title="When NUMCPU &gt; 0, CRSAS Ma1 implements two Message Handling Units (MHUs) to allow processors to interrupt each other to pass message. Two MHUs are provided so that it is possible for software to place one MHU in the Secure world and another in the Non-secure world. Both MHUs reside in the PD_SYS power domain and are reset using the nWARMRESETSYS.">
      Message Handling Unit
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
      0x5000_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_1FFF
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
     MHU1
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Message Handling Unit 1.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Message-Handling-Unit?lang=en" href="/documentation/102803/0000/Functional-Description/Message-Handling-Unit?lang=en" title="When NUMCPU &gt; 0, CRSAS Ma1 implements two Message Handling Units (MHUs) to allow processors to interrupt each other to pass message. Two MHUs are provided so that it is possible for software to place one MHU in the Secure world and another in the Non-secure world. Both MHUs reside in the PD_SYS power domain and are reset using the nWARMRESETSYS.">
      Message Handling Unit
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
      0x5000_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_3FFF
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
     DMA
     <sup>
      4
     </sup>
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
     DMA Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/DMA-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/DMA-registers?lang=en" title="CRSAS Ma1 implements up to one DMA-350. See Arm CoreLink DMA-350 Controller Technical Reference Manual for full details of the DMA software interface. Security and privilege checking of accesses to DMA registers are handled by the DMA.">
      DMA registers
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
      0x5000_4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_4FFF
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
     NPU0
     <sup>
      3
     </sup>
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
     NPU0 Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" title="CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm Ethos-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.">
      NPU&lt;m&gt; registers
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
      0x5000_5000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_5FFF
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
     NPU1
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     5
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU1 Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" title="CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm Ethos-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.">
      NPU&lt;m&gt; registers
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
      0x5000_6000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_6FFF
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
     NPU2
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU2 Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" title="CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm Ethos-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.">
      NPU&lt;m&gt; registers
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
      0x5000_7000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_7FFF
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
     NPU3
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     NPU3 Configuration interface
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en" title="CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm Ethos-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.">
      NPU&lt;m&gt; registers
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
      0x5000_8000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5000_FFFF
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
     Reserved (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
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
      0x5004_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5007_FFFF
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
     32
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_0FFF
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
     SACFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Secure Access Configuration Register Block.
    </p>
    <p>
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en" title="The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.">
      Secure access configuration register block
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     33
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_2FFF
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
     Reserved (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     34
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_3000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_3FFF
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
     VM0MPC
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
     S_PPC, P_PPC, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     VM0 Memory Protection Controller.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Volatile-Memory?lang=en" href="/documentation/102803/0000/Functional-Description/Volatile-Memory?lang=en" title="CRSAS Ma1 can support 0 to 4 volatile memory banks, VM&lt;x&gt;. The number of memory banks is defined by the NUMVMBANK configuration, and therefore x is 0 to NUMVMBANK-1, except when NUMVMBANK = 0 where there is no volatile memory bank.">
      Volatile memory
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     35
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_4FFF
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
     VM1MPC
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
     S_PPC, P_PPC, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     VM1 Memory Protection Controller.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Volatile-Memory?lang=en" href="/documentation/102803/0000/Functional-Description/Volatile-Memory?lang=en" title="CRSAS Ma1 can support 0 to 4 volatile memory banks, VM&lt;x&gt;. The number of memory banks is defined by the NUMVMBANK configuration, and therefore x is 0 to NUMVMBANK-1, except when NUMVMBANK = 0 where there is no volatile memory bank.">
      Volatile memory
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     36
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_5000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_5FFF
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
     VM2MPC
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
     S_PPC, P_PPC, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     VM2 Memory Protection Controller.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Volatile-Memory?lang=en" href="/documentation/102803/0000/Functional-Description/Volatile-Memory?lang=en" title="CRSAS Ma1 can support 0 to 4 volatile memory banks, VM&lt;x&gt;. The number of memory banks is defined by the NUMVMBANK configuration, and therefore x is 0 to NUMVMBANK-1, except when NUMVMBANK = 0 where there is no volatile memory bank.">
      Volatile memory
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     37
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_6000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_6FFF
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
     VM3MPC
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
     S_PPC, P_PPC, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     VM3 Memory Protection Controller.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/Volatile-Memory?lang=en" href="/documentation/102803/0000/Functional-Description/Volatile-Memory?lang=en" title="CRSAS Ma1 can support 0 to 4 volatile memory banks, VM&lt;x&gt;. The number of memory banks is defined by the NUMVMBANK configuration, and therefore x is 0 to NUMVMBANK-1, except when NUMVMBANK = 0 where there is no volatile memory bank.">
      Volatile memory
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     38
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_7000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5008_FFFF
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
     Reserved (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     39
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5009_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5009_3FFF
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16KB
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CryptoCell312
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S, UP
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CryptoCell 312.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en" href="/documentation/102803/0000/Functional-Description/CryptoCell/Has-Crypto-configuration?lang=en" title="When HASCRYPTO = 1, CryptoCell-312 exists in the system and therefore, any interfaces and configuration that are associated with CryptoCell-312 also exist.">
      Has-Crypto configuration
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     40
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5009_4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x500F_FFFF
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
     41
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_0FFF
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
     TIMER0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     14
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer 0.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" title="CRSAS Ma1 implements four timestamp-based timers in the system, TIMER&lt;x&gt; where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.">
      Timestamp-based timers registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     42
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_1FFF
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
     TIMER1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     15
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer 1.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" title="CRSAS Ma1 implements four timestamp-based timers in the system, TIMER&lt;x&gt; where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.">
      Timestamp-based timers registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     43
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_2FFF
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
     TIMER2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     16
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer 2.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" title="CRSAS Ma1 implements four timestamp-based timers in the system, TIMER&lt;x&gt; where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.">
      Timestamp-based timers registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     44
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_3000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_3FFF
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
     TIMER3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     17
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Timer 3.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en" title="CRSAS Ma1 implements four timestamp-based timers in the system, TIMER&lt;x&gt; where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See Secure access configuration register block.">
      Timestamp-based timers registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     45
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_4000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5800_FFFF
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
     Reserved (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     46
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5804_0000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5804_0FFF
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
     SWDCTRL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     S_PPC, P_PPC, P
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Secure Watchdog Control Frame. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en" title="CRSAS Ma1 implements two timestamp-based watchdogs in the system. All reside in the PD_SYS power domain and are reset by nWARMRESETSYS. One watchdog timer is Secure access only, while another is Non-secure. Each Watchdog Timer implements two register frames, a Control Frame and a Refresh Frame. The Control Frame is always fixed privileged while the Refresh Frame accessibility to unprivileged access is configurable and controlled by PPC0. See PERIPHSPPPC0 and PERIPHNSPPPC0.">
      Timestamp-based Watchdogs registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     47
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5804_1000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5804_1FFF
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
     SWDREF
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
     Secure Watchdog Refresh Frame. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en" href="/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en" title="CRSAS Ma1 implements two timestamp-based watchdogs in the system. All reside in the PD_SYS power domain and are reset by nWARMRESETSYS. One watchdog timer is Secure access only, while another is Non-secure. Each Watchdog Timer implements two register frames, a Control Frame and a Refresh Frame. The Control Frame is always fixed privileged while the Refresh Frame accessibility to unprivileged access is configurable and controlled by PPC0. See PERIPHSPPPC0 and PERIPHNSPPPC0.">
      Timestamp-based Watchdogs registers
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     48
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5804_2000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5804_FFFF
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
     Reserved (
     <span class="documents-archterm">
      RAZ/WI
     </span>
     )
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     49
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x5805_0000
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x580F_FFFF
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

1 The number of VM<i>MPC regions depends on NUMVMBANK. If VM<i> does not exist, then the VM<i>MPC region is Reserved.

2 MHU0 and MHU1 only exist if NUMCPU > 0.

3 NPUn only exists if NUMNPU > 0.

4 DMA only exists if NUMDMA = 1

- **[Message Handling Unit register map](/documentation/102803/0000/Programmers-model/Peripheral-Region/Message-Handling-Unit-register-map?lang=en)**
   The CRSAS Ma1 implements up to two Message Handling Units (MHUs). These allow software to raise interrupts to the CPU cores. Both MHUs are mapped twice into both Secure and Non-secure regions as follows, and a PPC then controls which area each MHU resides:
- **[Secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en)**
   The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 0x5008\_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.
- **[Non-secure Access Configuration Register Block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block?lang=en)**
   The Non-secure Access Configuration Register Block implements program visible states that allow software to control various security gating units within the design. This register block base address is 0x4008\_0000. These registers are Non-secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.
- **[Timestamp-based timers registers](/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-timers-registers?lang=en)**
   CRSAS Ma1 implements four timestamp-based timers in the system, TIMER<x> where x is 0 to 3. All timers are mapped to the Secure or Non-secure world through PPC0, which also controls accessibility of unprivileged accesses. See [Secure access configuration register block](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block?lang=en "The Secure Access Configuration Register Block implements program visible states that allow software to control security gating units within the design. The register block base address is 5008_0000. These registers are Secure privileged access only and support 32-bit RW accesses. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes are ignored.").
- **[Timestamp-based Watchdogs registers](/documentation/102803/0000/Programmers-model/Peripheral-Region/Timestamp-based-Watchdogs-registers?lang=en)**
   CRSAS Ma1 implements two timestamp-based watchdogs in the system. All reside in the PD\_SYS power domain and are reset by nWARMRESETSYS. One watchdog timer is Secure access only, while another is Non-secure. Each Watchdog Timer implements two register frames, a Control Frame and a Refresh Frame. The Control Frame is always fixed privileged while the Refresh Frame accessibility to unprivileged access is configurable and controlled by PPC0. See [PERIPHSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Secure-Access-Configuration-Register-Block/PERIPHSPPPC0?lang=en "Secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only allowed Secure privileged access or is allowed Secure unprivileged access as well. Each field defines this for an associated peripheral, by the following settings:") and [PERIPHNSPPPC0](/documentation/102803/0000/Programmers-model/Peripheral-Region/Non-secure-Access-Configuration-Register-Block/PERIPHNSPPPC0?lang=en "Non-secure Unprivileged Access Peripheral Interconnect Subordinate Peripheral Protection Controller Register allows software to configure if each Peripheral Interconnect peripheral that it controls through a PPC is only Non-secure privileged access or is allowed Non-secure unprivileged access as well.").
- **[DMA registers](/documentation/102803/0000/Programmers-model/Peripheral-Region/DMA-registers?lang=en)**
   CRSAS Ma1 implements up to one DMA-350. See Arm® CoreLink™ DMA-350 Controller Technical Reference Manual for full details of the DMA software interface. Security and privilege checking of accesses to DMA registers are handled by the DMA.
- **[NPU<m> registers](/documentation/102803/0000/Programmers-model/Peripheral-Region/NPU-m--registers?lang=en)**
   CRSAS Ma1 implements up to four Ethos-U55 NPUs. See Arm® Ethos™-U55 NPU Technical Reference Manual for full details of the NPU software interface. Security and privilege checking of accesses to NPU registers are handled by PPC0.
