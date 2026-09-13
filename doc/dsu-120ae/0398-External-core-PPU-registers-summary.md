# External core PPU registers summary

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary>

### External core PPU registers summary

Each core Power Policy Unit (PPU) in the DSU-120AE DynamIQ™ cluster has an individual set of Power Policy Unit (PPU) registers. Each set of registers is identical, and are memory-mapped onto the utility bus at different base addresses.

The summary table provides an overview of all the PPU registers for a single core in the DSU-120AE. For more information about a register, click on the register name in the table.

> ### Note
>
> - You must access the cluster system control registers from the Secure state.
> - The core PPU registers are treated as RAZ/WI if either:
>   - The register is marked as Reserved.
>   - The register is accessed in the wrong Security state.
> - Any address that is not documented is treated as RAZ/WI.
> - These register descriptions are configuration of the PPU architecture, see [Arm® Power Policy Unit Architecture Specification](https://developer.arm.com/documentation/den0051/latest) for more details.
> - The values for the core PPU registers are based on a typical multi-core cluster configuration, but these values might vary for different cluster configurations.
> - The base address for the core PPU registers is 0x<n>80000, where n is the core instance number. For example, for core 0 the PPU base address is 0x080000 and for core 1 the PPU base address is 0x180000.
> - For registers without a listed reset value refer to the individual field resets documented on the register description pages

<table class="documents-opcodes" id="ixj1733415042301__summary_table">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Core PPU register summary
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
   <th class="documents-nocellnorowborder" colspan="1" id="d48635e169" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48635e171" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48635e173" rowspan="1">
    Reset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48635e175" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d48635e177" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x000
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PWPR--Power-Policy-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PWPR--Power-Policy-Register?lang=en" title="This register enables software to program both power and operating mode policy. It also contains related settings including the enable for dynamic transitions and the lock enable.">
     PPU_PWPR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Power Policy Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x004
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PMER--Power-Mode-Emulation-Enable-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PMER--Power-Mode-Emulation-Enable-Register?lang=en" title="This register allows software to enable entry into emulated modes.">
     PPU_PMER
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Power Mode Emulation Enable Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x008
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PWSR--Power-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PWSR--Power-Status-Register?lang=en" title="This read-only register contains status information for the power mode, operating mode, dynamic transitions, and lock feature.">
     PPU_PWSR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Power Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x010
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-DISR--Device-Interface-Input-Current-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-DISR--Device-Interface-Input-Current-Status-Register?lang=en" title="This read-only register contains status reflecting the values of the device interface inputs.">
     PPU_DISR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device Interface Input Current Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x014
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-MISR--Miscellaneous-Input-Current-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-MISR--Miscellaneous-Input-Current-Status-Register?lang=en" title="This read-only register contains status reflecting the values of miscellaneous inputs.">
     PPU_MISR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Miscellaneous Input Current Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x018
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-STSR--Stored-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-STSR--Stored-Status-Register?lang=en" title="This register is reserved for P-Channel PPUs.">
     PPU_STSR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Stored Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x01C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-UNLK--Unlock-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-UNLK--Unlock-Register?lang=en" title="This register allows software to unlock the PPU from a locked power mode.">
     PPU_UNLK
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Unlock Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x020
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PWCR--Power-Configuration-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PWCR--Power-Configuration-Register?lang=en" title="This register controls enabling and disabling of hardware control inputs to the PPU.">
     PPU_PWCR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Power Configuration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x024
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PTCR--Power-Mode-Transition-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PTCR--Power-Mode-Transition-Register?lang=en" title="This register contains settings which affect the behaviour of certain power mode transitions.">
     PPU_PTCR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Power Mode Transition Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x030
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IMR--Interrupt-Mask-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IMR--Interrupt-Mask-Register?lang=en" title="This register controls the events that assert the interrupt output. Additional event masking controls are in the Additional Interrupt Mask Register (ext-PPU_AIMR), Input Edge Sensitivity Register (ext-PPU_IESR), and the Operating Mode Active Edge Sensitivity Register (ext-PPU_OPSR).">
     PPU_IMR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Interrupt Mask Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x034
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-AIMR--Additional-Interrupt-Mask-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-AIMR--Additional-Interrupt-Mask-Register?lang=en" title="This register controls the events that assert the interrupt output. Additional event masking controls are in the Interrupt Mask Register (PPU_IMR), Input Edge Sensitivity Register (PPU_IESR), and the Operating Mode Active Edge Sensitivity Register (PPU_OPSR).">
     PPU_AIMR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Additional Interrupt Mask Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x038
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-ISR--Interrupt-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-ISR--Interrupt-Status-Register?lang=en" title="This register contains information about events causing the assertion of the interrupt output. It is also used to clear interrupt events.">
     PPU_ISR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Interrupt Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x03C
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-AISR--Additional-Interrupt-Status-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-AISR--Additional-Interrupt-Status-Register?lang=en" title="This register contains information about events causing the assertion of the interrupt output. It is also used to clear interrupt events.">
     PPU_AISR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Additional Interrupt Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x040
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IESR--Input-Edge-Sensitivity-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IESR--Input-Edge-Sensitivity-Register?lang=en" title="This register configures the transitions on the power mode DEVPACTIVE inputs that generate an Input Edge interrupt event.">
     PPU_IESR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Input Edge Sensitivity Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x044
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-OPSR--Operating-Mode-Active-Edge-Sensitivity-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-OPSR--Operating-Mode-Active-Edge-Sensitivity-Register?lang=en" title="This register configures the transitions on the operating mode DEVPACTIVE inputs that generate an Input Edge interrupt event.">
     PPU_OPSR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Operating Mode Active Edge Sensitivity Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x050
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-FUNRR--Functional-Retention-RAM-Configuration-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-FUNRR--Functional-Retention-RAM-Configuration-Register?lang=en" title="This register is reserved.">
     PPU_FUNRR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Functional Retention RAM Configuration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x054
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-FULRR--Full-Retention-RAM-Configuration-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-FULRR--Full-Retention-RAM-Configuration-Register?lang=en" title="This register is reserved.">
     PPU_FULRR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Full Retention RAM Configuration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x058
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-MEMRR--Memory-Retention-RAM-Configuration-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-MEMRR--Memory-Retention-RAM-Configuration-Register?lang=en" title="This register is reserved.">
     PPU_MEMRR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Memory Retention RAM Configuration Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x170
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-DCDR0--Device-Control-Delay-Configuration-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-DCDR0--Device-Control-Delay-Configuration-Register-0?lang=en" title="This register is used to program device control delay parameters.">
     PPU_DCDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device Control Delay Configuration Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0x174
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-DCDR1--Device-Control-Delay-Configuration-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-DCDR1--Device-Control-Delay-Configuration-Register-1?lang=en" title="This register is used to program device control delay parameters.">
     PPU_DCDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device Control Delay Configuration Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFB0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IDR0--PPU-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IDR0--PPU-Identification-Register-0?lang=en" title="This read-only register contains information on the type and number of channels on the device interface and power and operating modes supported.">
     PPU_IDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFB4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IDR1--PPU-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IDR1--PPU-Identification-Register-1?lang=en" title="This read-only register contains information on the optional features and configurations that are supported by this PPU.">
     PPU_IDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFC8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IIDR--Implementation-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IIDR--Implementation-Identification-Register?lang=en" title="This register provides information about the implementer and implementation of the PPU.">
     PPU_IIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Implementation Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFCC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-AIDR--Architecture-Identification-Register?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-AIDR--Architecture-Identification-Register?lang=en" title="This register identifies the PPU architecture revision.">
     PPU_AIDR
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Architecture Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR4--PPU-Peripheral-Identification-Register-4?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR4--PPU-Peripheral-Identification-Register-4?lang=en" title="Provides CoreSight discovery information.">
     PPU_PIDR4
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Peripheral Identification Register 4
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR5--PPU-Peripheral-Identification-Register-5?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR5--PPU-Peripheral-Identification-Register-5?lang=en" title="Provides CoreSight discovery information.">
     PPU_PIDR5
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Peripheral Identification Register 5
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFD8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR6--PPU-Peripheral-Identification-Register-6?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR6--PPU-Peripheral-Identification-Register-6?lang=en" title="Provides CoreSight discovery information.">
     PPU_PIDR6
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Peripheral Identification Register 6
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFDC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR7--PPU-Peripheral-Identification-Register-7?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR7--PPU-Peripheral-Identification-Register-7?lang=en" title="Provides CoreSight discovery information.">
     PPU_PIDR7
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Peripheral Identification Register 7
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR0--PPU-Peripheral-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR0--PPU-Peripheral-Identification-Register-0?lang=en" title="Provides CoreSight discovery information.">
     PPU_PIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Peripheral Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR1--PPU-Peripheral-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR1--PPU-Peripheral-Identification-Register-1?lang=en" title="Provides CoreSight discovery information.">
     PPU_PIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Peripheral Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFE8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR2--PPU-Peripheral-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR2--PPU-Peripheral-Identification-Register-2?lang=en" title="Provides CoreSight discovery information.">
     PPU_PIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Peripheral Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR3--PPU-Peripheral-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-PIDR3--PPU-Peripheral-Identification-Register-3?lang=en" title="Provides CoreSight discovery information.">
     PPU_PIDR3
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Peripheral Identification Register 3
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-CIDR0--PPU-Component-Identification-Register-0?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-CIDR0--PPU-Component-Identification-Register-0?lang=en" title="Provides CoreSight discovery information.">
     PPU_CIDR0
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Component Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-CIDR1--PPU-Component-Identification-Register-1?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-CIDR1--PPU-Component-Identification-Register-1?lang=en" title="Provides CoreSight discovery information.">
     PPU_CIDR1
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Component Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0xFF8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-CIDR2--PPU-Component-Identification-Register-2?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-CIDR2--PPU-Component-Identification-Register-2?lang=en" title="Provides CoreSight discovery information.">
     PPU_CIDR2
    </a>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    PPU Component Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFFC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <a class="document-topic" document-topic-path="/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-CIDR3--PPU-Component-Identification-Register-3?lang=en" href="/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-CIDR3--PPU-Component-Identification-Register-3?lang=en" title="Provides CoreSight discovery information.">
     PPU_CIDR3
    </a>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    See individual bit resets.
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    32-bit
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    PPU Component Identification Register 3
   </td>
  </tr>
 </tbody>
</table>
