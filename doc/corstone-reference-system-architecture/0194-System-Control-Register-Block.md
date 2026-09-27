# System Control Register Block

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block>

### System Control Register Block

The System Control Register Block implements registers for power, clocks, resets, and other general system control. This module resides at base address 0x5802\_1000 in the Secure region. The System Control Register Block is Secure privileged access only. For write access to these registers, only 32-bit writes are supported. Any byte and halfword writes results in its write data ignored.

Most System Control registers reside in the PD\_MGMT power domain when PILEVEL = 2, or is merged into PD\_AON when PILEVEL < 2. When entering lower power states, some of the register values must be retained. How retention is achieved is IMPLEMENTATION DEFINED. Other registers not in PD\_MGMT reside instead in the PD\_AON domain.

The following table shows the details of this register block.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   System Control Register Map
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
   <th class="documents-nocellnorowborder" colspan="1" id="d30142e76" rowspan="1">
    <p>
     Offset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d30142e80" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d30142e84" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d30142e88" rowspan="1">
    <p>
     Reset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d30142e92" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d30142e97" rowspan="1">
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
     SECDBGSTAT
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Secure Debug Configuration Status Register.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGSTAT?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGSTAT?lang=en" title="Secure Debug Configuration Status Register.">
      SECDBGSTAT
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
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SECDBGSET
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
     Secure Debug Configuration Set Register.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGSET?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGSET?lang=en" title="Secure Debug Configuration Set Register.">
      SECDBGSET
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x008
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SECDBGCLR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     WO
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
     Secure Debug Configuration Clear Register.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGCLR?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers/SECDBGCLR?lang=en" title="The Secure Debug Configuration Clear Register.">
      SECDBGCLR
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SCSECCTRL
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
     System Control Security Controls Register. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/SCSECCTRL?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/SCSECCTRL?lang=en" title="The System Control Security Controls provides register bits to set the Secure Configuration lock of this register block.">
      SCSECCTRL
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x010
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CLK_CFG0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Register 0.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG0?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG0?lang=en" title="The CLK_CFG0 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.">
      CLK_CFG0
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x014
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CLK_CFG1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Register 1.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG1?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG1?lang=en" title="The CLK_CFG1 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.">
      CLK_CFG1
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x018
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CLOCK_FORCE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Clock Forces.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLOCK-FORCE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLOCK-FORCE?lang=en" title="The Clock Force register allows software to override dynamic clock gating that may be implemented in the system and keep each clock running.">
      CLOCK_FORCE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CLK_CFG2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Clock Configuration Register 1.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG2?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG2?lang=en" title="The CLK_CFG2 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.">
      CLK_CFG2
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x020
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0x0FF
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
      0x100
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RESET_SYNDROME
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
      0x0000_0001
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
     Reset syndrome.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/RESET-SYNDROME?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/RESET-SYNDROME?lang=en" title="The RESET_SYNDROME register stores the reason for the last Reset event. Writing HIGH to a bit results in that bit write value to be ignored and the bit maintaining its previous value. RESET_SYNDROME is cleared by software writing zero to each bit to clear. If after starting from a reset event, RESET_SYNDROME is not cleared, on another reset event, the register may no longer accurately reflect the last reset event. CPU&lt;n&gt;LOCKUP does not actually generate reset, but when HIGH, it indicates that a CPU has locked-up and could be a precursor to another reset event, for example, watchdog timer reset request.">
      RESET_SYNDROME
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x104
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RESET_MASK
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reset Mask.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/RESET-MASK?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/RESET-MASK?lang=en" title="The RESET_MASK register allows software to control which reset sources are going to be merged to generate the system wide warm reset, nWARMRESETAON, or the nCOLDRESETAON signal. Set each bit to HIGH to enable each source. Note that each of these mask bits, if cleared, not only prevents the reset source being used to generate the reset, it also prevents the associated RESET_SYNDROME register bit from recording the event.">
      RESET_MASK
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x108
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SWRESET
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     WO
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
     Software Reset.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/SWRESET?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/SWRESET?lang=en" title="The SWRESET register allows software to request for a system Cold reset. To request for a Cold reset, write &lsquo;1&rsquo; to the register. The register always returns zeros.">
      SWRESET
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x10C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     GRETREG
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
     General Purpose Retention Register.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/GRETREG?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/GRETREG?lang=en" title="The General Purpose Retention Register provides 16 bits of retention register for general storage, through HIBERANTION0 or HIBERNATION1 system power states.">
      GRETREG
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x110
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     INITSVTOR0
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU 0 Initial Secure Reset Vector Register.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en" title="The INITSVTOR&lt;n&gt; register is used to define the CPU &lt;n&gt; Initial Secure Vector table offset (VTOR_S.TBLOFF[31:7]) out of reset.">
      INITSVTOR&lt;n&gt;
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x114
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     INITSVTOR1
     <sup>
      1
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU 1 Initial Secure Reset Vector Register.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en" title="The INITSVTOR&lt;n&gt; register is used to define the CPU &lt;n&gt; Initial Secure Vector table offset (VTOR_S.TBLOFF[31:7]) out of reset.">
      INITSVTOR&lt;n&gt;
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x118
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     INITSVTOR2
     <sup>
      2
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU 2 Initial Secure Reset Vector Register.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en" title="The INITSVTOR&lt;n&gt; register is used to define the CPU &lt;n&gt; Initial Secure Vector table offset (VTOR_S.TBLOFF[31:7]) out of reset.">
      INITSVTOR&lt;n&gt;
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x11C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     INITSVTOR3
     <sup>
      3
     </sup>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU 3 Initial Secure Reset Vector Register.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en" title="The INITSVTOR&lt;n&gt; register is used to define the CPU &lt;n&gt; Initial Secure Vector table offset (VTOR_S.TBLOFF[31:7]) out of reset.">
      INITSVTOR&lt;n&gt;
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x120
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPUWAIT
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU Boot Wait Control.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CPUWAIT?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CPUWAIT?lang=en" title="The CPUWAIT register provides controls to force each CPU to wait after reset rather than Boot Immediately. This allows another entity in the expansion system or the debugger to access the system prior to the CPU booting.">
      CPUWAIT
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x124
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NMI_ENABLE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Enabling and Disabling Non Maskable Interrupts.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/NMI-ENABLE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/NMI-ENABLE?lang=en" title="The NMI_ENABLE register provides controls to enable or disable the internally or externally generated Non-Maskable Interrupt sources from generating an NMI interrupt on each CPU core. This allows a CPU to take control of all internal NMI interrupt sources or allow all CPUs to see the same NMI interrupts.">
      NMI_ENABLE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x128
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PPUINTSTAT
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
     PPU Interrupt Status. See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PPUINTSTAT?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PPUINTSTAT?lang=en" title="The PPU Interrupt Status Register brings together all PPU interrupt statuses in to a single register.">
      PPUINTSTAT
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x12C
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0x1F8
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
      0x1FC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PWRCTRL
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
      0x0000_0003
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
     Power Configuration and Control.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PWRCTRL?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PWRCTRL?lang=en" title="The Power Control register configures the power control features in CRSAS Ma1 System.">
      PWRCTRL
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x200
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_SYS_ SENSE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PDCM PD_SYS Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-SYS-SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-SYS-SENSE?lang=en" title="The Power Dependency Control Matrix System Power domain (PD_SYS) Sensitivity register is used to define what keeps the PD_SYS domain awake and the minimum power state to use when the domain is in its low power state.">
      PDCM_PD_SYS_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x204
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_CPU0_ SENSE
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
     PDCM PD_CPU0 Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en" title="The Power Dependency Control Matrix CPU &lt;n&gt; Power domain (PD_CPU&lt;n&gt;) Sensitivity register is used to define what keeps the PD_CPU&lt;n&gt; domain awake.">
      PDCM_PD_CPU&lt;n&gt;_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x208
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_CPU1_ SENSE
     <sup>
      1
     </sup>
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
     PDCM PD_CPU1 Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en" title="The Power Dependency Control Matrix CPU &lt;n&gt; Power domain (PD_CPU&lt;n&gt;) Sensitivity register is used to define what keeps the PD_CPU&lt;n&gt; domain awake.">
      PDCM_PD_CPU&lt;n&gt;_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x20C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_CPU2_ SENSE
     <sup>
      2
     </sup>
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
     PDCM PD_CPU2 Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en" title="The Power Dependency Control Matrix CPU &lt;n&gt; Power domain (PD_CPU&lt;n&gt;) Sensitivity register is used to define what keeps the PD_CPU&lt;n&gt; domain awake.">
      PDCM_PD_CPU&lt;n&gt;_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x210
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_CPU3_ SENSE
     <sup>
      3
     </sup>
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
     PDCM PD_CPU3 Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en" title="The Power Dependency Control Matrix CPU &lt;n&gt; Power domain (PD_CPU&lt;n&gt;) Sensitivity register is used to define what keeps the PD_CPU&lt;n&gt; domain awake.">
      PDCM_PD_CPU&lt;n&gt;_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x214
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_VMR0_ SENSE
     <sup>
      4
     </sup>
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
      0x4000_0000
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
     PDCM PD_VMR0 Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en" title="The Power Dependency Control Matrix Volatile Memory Region &lt;x&gt; Power domain (PD_VMR&lt;x&gt;) Sensitivity register is used to define what keeps awake the PD_VMR&lt;x&gt; domain and the minimum power state to use when the domain is in its low power state, where x is 0 to NUMVMBANK-1.">
      PDCM_PD_VMR&lt;x&gt;_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x218
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_VMR1_ SENSE
     <sup>
      5
     </sup>
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
      0x4000_0000
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
     PDCM PD_VMR1 Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en" title="The Power Dependency Control Matrix Volatile Memory Region &lt;x&gt; Power domain (PD_VMR&lt;x&gt;) Sensitivity register is used to define what keeps awake the PD_VMR&lt;x&gt; domain and the minimum power state to use when the domain is in its low power state, where x is 0 to NUMVMBANK-1.">
      PDCM_PD_VMR&lt;x&gt;_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x21C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_VMR2_ SENSE
     <sup>
      6
     </sup>
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
      0x4000_0000
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
     PDCM PD_VMR2 Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en" title="The Power Dependency Control Matrix Volatile Memory Region &lt;x&gt; Power domain (PD_VMR&lt;x&gt;) Sensitivity register is used to define what keeps awake the PD_VMR&lt;x&gt; domain and the minimum power state to use when the domain is in its low power state, where x is 0 to NUMVMBANK-1.">
      PDCM_PD_VMR&lt;x&gt;_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x220
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_VMR3_ SENSE
     <sup>
      7
     </sup>
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
      0x4000_0000
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
     PDCM PD_VMR3 Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en" title="The Power Dependency Control Matrix Volatile Memory Region &lt;x&gt; Power domain (PD_VMR&lt;x&gt;) Sensitivity register is used to define what keeps awake the PD_VMR&lt;x&gt; domain and the minimum power state to use when the domain is in its low power state, where x is 0 to NUMVMBANK-1.">
      PDCM_PD_VMR&lt;x&gt;_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x224
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0x248
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
      0x24C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCM_PD_MGMT_ SENSE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFG_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32-bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     PDCM PD_MGMT Sensitivity.
    </p>
    <p>
     See
     <a class="document-topic" document-topic-path="/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-MGMT-SENSE?lang=en" href="/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-MGMT-SENSE?lang=en" title="The Power Dependency Control Matrix PD_MGMT Power Domain Sensitivity register is used to define what keeps the PD_MGMT domains awake.">
      PDCM_PD_MGMT_SENSE
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x250
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
     Reserved Future RSS / system state retention
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
      0x0000_0054
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
      0x0000_004B
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

1 These registers do not exist and are reserved if NUMCPU < 1:

- PDCM\_PD\_CPU1\_SENSE
- INITSVTOR0
- INITSVTOR1

2 These registers do not exist and are reserved if NUMCPU < 2:

- INITSVTOR2
- PDCM\_PD\_CPU2\_SENSE

3 These registers do not exist and are reserved if NUMCPU < 3:

- INITSVTOR3
- PDCM\_PD\_CPU3\_SENSE

4 These registers do not exist and are reserved if NUMVMBANK < 1:

- PDCM\_PD\_VMR0\_SENSE

5 These registers do not exist and are reserved if NUMVMBANK < 2:

- PDCM\_PD\_VMR1\_SENSE

6 These registers do not exist and are reserved if NUMVMBANK < 3:

- PDCM\_PD\_VMR2\_SENSE

7 These registers do not exist and are reserved if NUMVMBANK < 4:

- PDCM\_PD\_VMR3\_SENSE

- **[Secure Debug Configuration Registers](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/Secure-Debug-Configuration-Registers?lang=en)**
   The Secure Debug Configuration Registers are used to select the source value for the Secure Debug Authentication, DBGEN, NIDEN, SPIDEN, SPNIDEN, DAPACCEN, and Debug Access Controls, DAPDSSACCEN, SYSDSSACCENX, and SYSDSSACCEN<n>. For each signal and just one for all SYSDSSACCEN<n> and SYSDSSACCENX, a selector is provided to select between an internal register value and the value on the boundary of the subsystem.
- **[SCSECCTRL](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/SCSECCTRL?lang=en)**
   The System Control Security Controls provides register bits to set the Secure Configuration lock of this register block.
- **[CLK\_CFG0](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG0?lang=en)**
   The CLK\_CFG0 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.
- **[CLK\_CFG1](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG1?lang=en)**
   The CLK\_CFG1 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.
- **[CLK\_CFG2](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLK-CFG2?lang=en)**
   The CLK\_CFG2 register provides control register fields to drive expansion clock generation logic that drives clock for this subsystem.
- **[CLOCK\_FORCE](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CLOCK-FORCE?lang=en)**
   The Clock Force register allows software to override dynamic clock gating that may be implemented in the system and keep each clock running.
- **[RESET\_SYNDROME](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/RESET-SYNDROME?lang=en)**
   The RESET\_SYNDROME register stores the reason for the last Reset event. Writing HIGH to a bit results in that bit write value to be ignored and the bit maintaining its previous value. RESET\_SYNDROME is cleared by software writing zero to each bit to clear. If after starting from a reset event, RESET\_SYNDROME is not cleared, on another reset event, the register may no longer accurately reflect the last reset event. CPU<n>LOCKUP does not actually generate reset, but when HIGH, it indicates that a CPU has locked-up and could be a precursor to another reset event, for example, watchdog timer reset request.
- **[RESET\_MASK](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/RESET-MASK?lang=en)**
   The RESET\_MASK register allows software to control which reset sources are going to be merged to generate the system wide warm reset, nWARMRESETAON, or the nCOLDRESETAON signal. Set each bit to HIGH to enable each source. Note that each of these mask bits, if cleared, not only prevents the reset source being used to generate the reset, it also prevents the associated RESET\_SYNDROME register bit from recording the event.
- **[SWRESET](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/SWRESET?lang=en)**
   The SWRESET register allows software to request for a system Cold reset. To request for a Cold reset, write ‘1’ to the register. The register always returns zeros.
- **[GRETREG](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/GRETREG?lang=en)**
   The General Purpose Retention Register provides 16 bits of retention register for general storage, through HIBERANTION0 or HIBERNATION1 system power states.
- **[INITSVTOR<n>](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/INITSVTOR-n-?lang=en)**
   The INITSVTOR<n> register is used to define the CPU <n> Initial Secure Vector table offset (VTOR\_S.TBLOFF[31:7]) out of reset.
- **[CPUWAIT](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/CPUWAIT?lang=en)**
   The CPUWAIT register provides controls to force each CPU to wait after reset rather than Boot Immediately. This allows another entity in the expansion system or the debugger to access the system prior to the CPU booting.
- **[NMI\_ENABLE](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/NMI-ENABLE?lang=en)**
   The NMI\_ENABLE register provides controls to enable or disable the internally or externally generated Non-Maskable Interrupt sources from generating an NMI interrupt on each CPU core. This allows a CPU to take control of all internal NMI interrupt sources or allow all CPUs to see the same NMI interrupts.
- **[PPUINTSTAT](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PPUINTSTAT?lang=en)**
   The PPU Interrupt Status Register brings together all PPU interrupt statuses in to a single register.
- **[PWRCTRL](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PWRCTRL?lang=en)**
   The Power Control register configures the power control features in CRSAS Ma1 System.
- **[PDCM\_PD\_SYS\_SENSE](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-SYS-SENSE?lang=en)**
   The Power Dependency Control Matrix System Power domain (PD\_SYS) Sensitivity register is used to define what keeps the PD\_SYS domain awake and the minimum power state to use when the domain is in its low power state.
- **[PDCM\_PD\_CPU<n>\_SENSE](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-CPU-n--SENSE?lang=en)**
   The Power Dependency Control Matrix CPU <n> Power domain (PD\_CPU<n>) Sensitivity register is used to define what keeps the PD\_CPU<n> domain awake.
- **[PDCM\_PD\_VMR<x>\_SENSE](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE?lang=en)**
   The Power Dependency Control Matrix Volatile Memory Region <x> Power domain (PD\_VMR<x>) Sensitivity register is used to define what keeps awake the PD\_VMR<x> domain and the minimum power state to use when the domain is in its low power state, where x is 0 to NUMVMBANK-1.
- **[PDCM\_PD\_MGMT\_SENSE](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-MGMT-SENSE?lang=en)**
   The Power Dependency Control Matrix PD\_MGMT Power Domain Sensitivity register is used to define what keeps the PD\_MGMT domains awake.
