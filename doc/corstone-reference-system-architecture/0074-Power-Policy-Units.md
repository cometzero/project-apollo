# Power Policy Units

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Power-Policy-Units>

### Power Policy Units

CRSAS Ma1 leverages Power Policy Units (PPUs) for power control for each Bounded Region (BR) in the system. Each BR is a collection of power domains where their power states are controlled collectively, usually by a PPU. The following table lists the mandatory configurations of all PPUs in the system, which BR each controls, and what power domain each resides in. Other PPU configurations that are not listed here are IMPLEMENTATION DEFINED. For more information on Power Policy Units, see Arm® Power Policy Unit Architecture Specification and Arm® CoreLink™ PCK-600 Power Control Kit Technical Reference Manual.

### Bounded Region Controlled by PPU

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Power Policy Unit Associations and Mandated Configurations
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
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d23771e91" rowspan="1">
    <p>
     PPU configuration
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d23771e95" rowspan="1">
    <p>
     MGMT_PPU
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d23771e99" rowspan="1">
    <p>
     DEBUG_PPU
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d23771e103" rowspan="1">
    <p>
     SYS_PPU
     <sup>
      4
     </sup>
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d23771e109" rowspan="1">
    <p>
     CPU&lt;n&gt;_PPU
     <sup>
      3
     </sup>
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d23771e116" rowspan="1">
    <p>
     NPU&lt;m&gt;_PPU
     <sup>
      6
     </sup>
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d23771e122" rowspan="1">
    <p>
     CRYPTO_PPU
     <sup>
      1
     </sup>
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Bounded Region Controlled by PPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BR_MGMT
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BR_DEBUG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BR_SYS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BR_CPU&lt;n&gt;
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BR_NPU&lt;m&gt;
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     BR_CRYPTO
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Power domain the PPU resides in
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PD_AON
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="5" rowspan="1">
    <p>
     PD_MGMT
     <sup>
      2
     </sup>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reset signal used by the PPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETAON
      </span>
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="5" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETMGMT
      </span>
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Device interface type
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     P-Channel
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="5" rowspan="1">
    <p>
     P-Channel
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Default power policy (DEF_PWR_POLICY)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ON/OFF
     <sup>
      5
     </sup>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="5" rowspan="1">
    <p>
     OFF
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Default power mode dynamic transition enable (DEF_PWR_DYN_EN)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="5" rowspan="1">
    <p>
     1
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Dynamic support
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
    <p>
     WARM_RST
    </p>
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
    <p>
     WARM_RST
    </p>
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
    <p>
     FULL_RET
    </p>
    <p>
     MEM_RST
    </p>
    <p>
     WARM_RST
    </p>
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
    <p>
     FULL_RET
    </p>
    <p>
     MEM_RST
    </p>
    <p>
     MEM_OFF
    </p>
    <p>
     FUNC_RST
    </p>
    <p>
     LOGIC_RST
    </p>
    <p>
     WARM_RST
    </p>
    <p>
     OFF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
    <p>
     WARM_RST
    </p>
    <p>
     OFF
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     ON
    </p>
    <p>
     WARM_RST
    </p>
    <p>
     OFF
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Default Operating Policy (DEF_OP_POLICY)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Number of Operating Modes (NUM_OPMODE_CFG)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
     <sup>
      NUMVMBANK
     </sup>
     -1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Operating Mode Active configuration (OP_ACTIVE_CFG)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1 if NUMVMBANK &gt; 0, else 0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Default Operating Mode Dynamic Transition Enable (DEF_OP_DYN_EN)
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1 if NUMVMBANK &gt; 0, else 0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Default Perform Device Interface Handshake When Transition from ON to WARM_RST mode Enable (WARM_RST_DEVREQEN_CFG)
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
  </tr>
 </tbody>
</table>

1 This PPU only exist when HASCRYPTO = 1 and PILEVEL > 0

2 If PILEVEL < 2 PD\_MGMT is merged into PD\_AON.

3 If PILEVEL = 0, then CPU0\_PPU is renamed as SYS\_PPU

4 If PILEVEL = 0, this SYS\_PPU column does not exist, while CPU0\_PPU is renamed as SYS\_PPU.

5 OFF when PILEVEL = 2, else ON

6 This PPU only exist when NUMNPU > 0

The PPUs are mapped to secure address space as defined in [System Control Peripheral Region](/documentation/102803/0000/Programmers-model/System-Control-Peripheral-Region?lang=en "The System Control Peripheral Regions are a collection of memory regions where system control related peripherals are mapped. These peripherals reside either in the PD_AON domain or in the PD_MGMT domain if PILEVEL = 2. There are four regions in total as follows:"). The write accessibility of PPU registers is controlled through the PWRCTRL.PPU\_ACCESS\_FILTER. When it is set to ‘1’, the system blocks all write accesses to the PPUs, by ignoring the writes, except for the following registers if they exist for each PPU:

- Interrupt Mask Register, at address offset 0x030
- Additional Interrupt Mask Register, at address offset 0x034
- Interrupt Status Register, at address 0x038
- Additional Interrupt Status Register, at address 0x03C

Access to the PPU is normally not required for normal operation because CRSAS Ma1 is architected to use the PPU primarily in dynamic mode, where the request to enter or leave a power state is managed and handshake using the PPU’s Device interface. Hence the only time access to PPUs might be required is for debug purposes.

When PWRCTRL.PPU\_ACCESS\_FILTER is set to ‘0’, all PPU registers are freely accessible to the secure world.
