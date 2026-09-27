# Configuration options

Source: <https://developer.arm.com/documentation/102803/latest/Configuration-options>

### Configuration options

The CRSAS Ma1 specification is configurable, which allow systems based on this specification to scale across the performance, power, and area requirement of the market.

An implementation of CRSAS Ma1 can support a subset of the configuration options defined here. An implementation of the subsystem, however, cannot support additional configuration options unless they are limited to micro-architectural features and are features that are orthogonal to existing configuration. Because of this, an implementation cannot add additional legal values to existing configuration options. The method by which the configurations are supported is IMPLEMENTATION DEFINED.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CRSAS Ma1 configurations
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d78408e65" rowspan="1">
    <p>
     Configuration option name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d78408e69" rowspan="1">
    <p>
     Legal values
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d78408e73" rowspan="1">
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
     NUMCPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-3
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It describes the number of Cortex-M CPU cores in the subsystem. The number of cores is equal to NUMCPU + 1.
    </p>
    <p>
     When PILEVEL = 0, NUMCPU must be set to &lsquo;0&rsquo;.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;TYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 3, 4
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Describes the type of CPU that is integrated:
    </p>
    <ul>
     <li>
      <p>
       0: Not implemented
      </p>
     </li>
     <li>
      <p>
       3: Cortex-M55
      </p>
     </li>
     <li>
      <p>
       4: Cortex-M85
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
    <p>
     CPU0TYPE must not be &lsquo;0&rsquo; and sparse CPUs are not supported. Therefore CPU0TYPE to CPU&lt;NUMCPU&gt;TYPE must not be &rsquo;0&rsquo;s.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NUMNPU
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-4
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Describes the number of Ethos NPU cores in the subsystem. The number of cores is equal to NUMNPU.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU&lt;m&gt;TYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Describes the type of NPU that is integrated, if any:
    </p>
    <ul>
     <li>
      <p>
       0: Not implemented
      </p>
     </li>
     <li>
      <p>
       1: Ethos-U55
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
    <p>
     This configuration option must exist when NUMNPU != 0.
    </p>
    <p>
     Sparse NPUs are not supported. Therefore, NPU0TYPE must not be &rsquo;0&rsquo;s.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU&lt;m&gt;PORSLRST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Describes the default security level that each NPU resets to.
    </p>
    <ul>
     <li>
      <p>
       0: Secure State
      </p>
     </li>
     <li>
      <p>
       1: Non-secure State
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
    <p>
     This configuration option must exist when NUMNPU != 0.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NPU&lt;m&gt;PORPLRST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Describes the default privilege level that each NPU resets to.
    </p>
    <ul>
     <li>
      <p>
       0: Unprivileged State
      </p>
     </li>
     <li>
      <p>
       1: Privileged State
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
    <p>
     This configuration option only exists when NUMNPU != 0.
    </p>
    <p>
     We recommend that this is set to 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NUMDMA
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Describes the number of DMA cores present in the system.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DMATYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Describes the type of DMA that is integrated:
    </p>
    <ul>
     <li>
      <p>
       0: Not implemented
      </p>
     </li>
     <li>
      <p>
       1: DMA-350
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
    <p>
     This configuration option must exist when NUMDMA != 0.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PILEVEL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1, 2
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Power Infrastructure Level. Defines the implemented power structure of the system:
    </p>
    <ul>
     <li>
      <p>
       0: Basic Power Structure
      </p>
     </li>
     <li>
      <p>
       1: Intermediate Power Structure
      </p>
     </li>
     <li>
      <p>
       2: Advance Power infrastructure
      </p>
     </li>
     <li>
      <p>
       Others: Reserved
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NUMVMBANK
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-4
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Selects the number of Volatile Memory Banks.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     VMADDRWIDTH
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     14 to (24- ceil(log
     <sub>
      2
     </sub>
     (NUMVMBANK)))
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Defines the address width for all Volatile Memory Banks when NUMVMBANK &gt; 0. This then defines the size of each bank as 2
     <sup>
      VMADDRWIDTH
     </sup>
     bytes.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     VMMPCBLKSIZE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3-15
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Defines the Block size of the MPC associated with all Volatile Memory Banks. Volatile Memory Block size = 2
     <sup>
      (VMMPCBLKSIZE + 5)
     </sup>
     bytes.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     HASCRYPTO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Defines whether CryptoCell-312 is included.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     HASCSS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Defines whether the CoreSight SoC-600 based Debug infrastructure is included.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes
      </p>
     </li>
    </ul>
    <p>
     HASCSS must be to 1 when NUMCPU &gt; 0.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     HASCPU&lt;n&gt;IWIC
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Defines if each CPU has IWIC.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PDCMQCHWIDTH
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0-4
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It selects the width of Power Dependency Control Matrix Q-Channel interface that the system supports.
    </p>
    <p>
     When set to &lsquo;0&rsquo;, the Power Dependency Control Matrix Q-Channel interface does not exist.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     INITSVTOR&lt;n&gt;RST[31:7]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Any address values that resides in Secure world and is executable.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The value of CPU &lt;n&gt; Secure Vector table offset address register in the System Control Register.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DBGENSELDIS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     When HASCRYPTO = 1, the only legal value is 1. Else, both 0 and 1 are legal.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The DBGEN Selector Disable.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes, force DBGEN to use DBGENIN
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NIDENSELDIS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     When HASCRYPTO = 1, the only legal value is 1. Else, both 0 and 1 are legal.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The NIDEN Selector Disable.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes, force NIDEN to use NIDENIN
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SPIDENSELDIS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     When HASCRYPTO = 1, the only legal value is 1. Else, both 0 and 1 are legal.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The SPIDEN Selector Disable.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes. force SPIDEN to use SPIDENIN
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SPNIDENSELDIS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     When HASCRYPTO = 1, the only legal value is 1. Else, both 0 and 1 are legal.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The SPNIDEN Selector Disable.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes, force SPNIDEN to use SPNIDENIN
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DAPACCENSELDIS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     When HASCRYPTO = 1, the only legal value is 1. Else, both 0 and 1 are legal.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The DAPACCEN Selector Disable.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes, force DAPACCEN to use DAPACCENIN
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DAPDSSACCENSELDIS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     When HASCRYPTO = 1, the only legal value is 1 only. Else, both 0 and 1 are legal.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The DAPDSSACCEN Selector Disable.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes, force DAPDSSACCEN to use DAPDSSACCENIN
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SYSDSSACCENSELDIS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     When HASCRYPTO = 1, the only legal value is 1. Else, both 0 and 1 are legal.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The SYSDSSACCEN Selector Disable.
    </p>
    <ul>
     <li>
      <p>
       0: No
      </p>
     </li>
     <li>
      <p>
       1: Yes, force SYSDSSACCEN&lt;n&gt; and SYSDSSACCENX to use SYSDSSACCENIN&lt;n&gt; and SYSDSSACCENXIN respectively.
      </p>
     </li>
    </ul>
    <p>
     This configuration option must exist when HASCSS = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     NSMSCEXPRST[15:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1 for each bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The reset value for NSMSCEXP.NS_MSCEXP[15:0]. This value defines the security world of each expansion MSC when the PD_SYS power domain is powered up or is reset. It defines up to 16 MSCs, where each bit is:
    </p>
    <ul>
     <li>
      <p>
       0: Secure
      </p>
     </li>
     <li>
      <p>
       1: Non-secure
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ACCWAITNRST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The reset value of Bus access wait at reset. This defines whether the system blocks access from expansion managers that implement access gating into the Main and Peripheral Interconnect when the PD_SYS power domain is powered up or is reset.
    </p>
    <ul>
     <li>
      <p>
       0: Blocks access
      </p>
     </li>
     <li>
      <p>
       1: Allows access
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;EXPNUMIRQ
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Zero to Maximum number of interrupts the CPU can support, minus 32.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It specifies the number of expansion interrupts for each CPU.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;EXPIRQDIS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     One bit per expansion interrupt, with each set to &lsquo;0&rsquo; or &lsquo;1&rsquo;.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It specifies for each CPU whether each expansion interrupt bit is implemented or disabled.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;INTNMIENABLERST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It specifies the Warm reset value of NMI_ENABLE.CPU&lt;n&gt;_INTNMI_ENABLE. This determines whether the internally generated interrupt sources can raise the NMI interrupt on each CPU:
    </p>
    <ul>
     <li>
      <p>
       0: Internal NMI sources are masked from driving NMI
      </p>
     </li>
     <li>
      <p>
       1: Interrupt NMI sources can drive NMI
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;EXPNMIENABLERST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It specifies the Warm reset value of NMI_ENABLE.CPU&lt;n&gt;_EXPNMI_ENABLE. This determines whether the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;EXPNMI
      </span>
     </span>
     top level pin is able to raise an NMI interrupt on each CPU:
    </p>
    <ul>
     <li>
      <p>
       0:
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         CPU&lt;n&gt;EXPNMI
        </span>
       </span>
       is masked from driving NMI.
      </p>
     </li>
     <li>
      <p>
       1:
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         CPU&lt;n&gt;EXPNMI
        </span>
       </span>
       is allowed to drive NMI.
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;WAITRST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The (Primary) wait of the CPU at boot control register CPU&lt;n&gt;WAIT reset value.
    </p>
    <ul>
     <li>
      <p>
       0: Boot normally
      </p>
     </li>
     <li>
      <p>
       1: Wait at boot
      </p>
     </li>
    </ul>
    <p>
     We recommend that this is set to &lsquo;0&rsquo;, unless there are other reasons in the system or SoC to initially stop a processor from booting post reset. For example, there may be another higher security entity in the SoC that wants access to the system prior to allowing the CPUs to boot.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;CPUIDRST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the SoC integrator.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     A unique identity value defined for each CPU in the system. Defines the values read at each CPU &lt;n&gt; local&rsquo;s CPU&lt;n&gt;_IDENTITY.CPUID register. Legal values are within 0 to 15, inclusive.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     LOCKDCAIC
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Disable access to all processor&rsquo;s instruction cache direct cache access registers DCAICLR and DCAICRR. Asserting this signal prevents direct access to the instruction cache Tag or Data RAM content. This is required when using eXecutable Only Memory (XOM).
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     COLDRESET_MODE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Cold Reset Mode. It defines if the watchdog timeouts,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       RESETREQ
      </span>
     </span>
     signal, and writes to the SWRESET register can be used to trigger a system Cold reset and therefore drive
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       nCOLDRESETAON
      </span>
     </span>
     :
    </p>
    <ul>
     <li>
      <p>
       0: Watchdogs,
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         RESETREQ
        </span>
       </span>
       signal, and the SWRESETREQ register value contributes to Cold Reset.
      </p>
     </li>
     <li>
      <p>
       1: Watchdogs,
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         RESETREQ
        </span>
       </span>
       signal, and the SWRESETREQ register value does not contribute to Cold Reset.
      </p>
     </li>
    </ul>
    <p>
     When set to &lsquo;1&rsquo;, an entity outside the subsystem is expected to observe the following signals to decide when to drive
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       HOSTRESETREQ
      </span>
     </span>
     :
    </p>
    <ul>
     <li>
      <p>
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         NSWDRSTREQSTATUS
        </span>
       </span>
      </p>
     </li>
     <li>
      <p>
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         SWDRSTREQSTATUS
        </span>
       </span>
      </p>
     </li>
     <li>
      <p>
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         SSWDRSTREQSTATUS
        </span>
       </span>
      </p>
     </li>
     <li>
      <p>
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         RESETREQSTATUS
        </span>
       </span>
      </p>
     </li>
     <li>
      <p>
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         SWRSTREQSTATUS
        </span>
       </span>
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DEBUGLEVEL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1, 2
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It selects the debug level of the subsystem:
    </p>
    <ul>
     <li>
      <p>
       0: Debug System does not exist. There is no Debug Access and no Trace support.
      </p>
     </li>
     <li>
      <p>
       1: Debug system exists without Trace support. Debug Access Interface(s) exists, but Trace is not supported.
      </p>
     </li>
     <li>
      <p>
       2: Debug system exists with Trace support. Both Debug Access Interface(s) and Trace Interface exist.
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MPCEXPDIS[15:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1 for each bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It disables support for individual bits on the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMPCEXPSTATUS
      </span>
     </span>
     bus. If MPCEXPDIS[i] = 1&rsquo;b1, then either
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMPCEXPSTATUS[i]
      </span>
     </span>
     does not exist, or if it does exist, is not used.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MSCEXPDIS[15:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1 for each bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It disables support for individual bits on the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPSTATUS
      </span>
     </span>
     ,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPCLEAR
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NSMSCEXP
      </span>
     </span>
     buses. If MSCEXPDIS[i] = 1&rsquo;b1, then either
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPSTATUS[i]
      </span>
     </span>
     ,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPCLEAR[i]
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NSMSCEXP[i]
      </span>
     </span>
     does not exist, or if they do exist,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPSTATUS[i]
      </span>
     </span>
     is not used,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SMSCEXPCLEAR[i]
      </span>
     </span>
     are tied LOW and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       NSMSCEXP[i]
      </span>
     </span>
     are tied HIGH.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BRGEXPDIS[15:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1 for each bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It disables support for individual bits on the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       BRGEXPSTATUS
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       BRGEXPCLEAR
      </span>
     </span>
     buses. If
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       BRGEXPDIS[i]
      </span>
     </span>
     = 1&rsquo;b1, then either
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       BRGEXPSTATUS[i]
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       BRGEXPCLEAR[i]
      </span>
     </span>
     does not exist, or if they do exist,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       BRGEXPSTATUS[i]
      </span>
     </span>
     is not used and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       BRGEXPCLEAR[i]
      </span>
     </span>
     are tied LOW.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PERIPHPPCEXP{0-3}DIS[15:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1 for each bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It disables support for individual bits on the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHNSPPCEXP{0-3}
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHPPPCEXP{0-3}
      </span>
     </span>
     buses. If PERIPHPPCEXP{0-3}DIS[i] = 1&rsquo;b1, then either
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHNSPPCEXP{0-3}[i]
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHPPPCEXP{0-3}[i]
      </span>
     </span>
     does not exist, or if they do exist,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHNSPPCEXP{0-3}[i]
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PERIPHPPPCEXP{0-3}[i]
      </span>
     </span>
     are not used and tied LOW.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MAINPPCEXP{0-3}DIS[15:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1 for each bit
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It disables support for individual bits on the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINNSPPCEXP{0-3}
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINPPPCEXP{0-3}
      </span>
     </span>
     buses. If MAINPPCEXP{0-3}DIS[i] = 1&rsquo;b1, then either
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINNSPPCEXP{0-3}[i]
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINPPPCEXP{0-3}[i]
      </span>
     </span>
     does not exist, or if they do,
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINNSPPCEXP{0-3}[i]
      </span>
     </span>
     and
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       MAINPPPCEXP{0-3}[i]
      </span>
     </span>
     are not used and tied LOW.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;CLKCFGRST[3:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0xF
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CLK_CFG0.CPU&lt;n&gt;CLKCFG reset value. CPU&lt;n&gt;CLKCFGRST defines the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLKCFG
      </span>
     </span>
     output expected to be used for clock divider or generation configuration of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CPU&lt;n&gt;CLK
      </span>
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SYSCLKCFGRST[3:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0xF
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CLK_CFG1.SYSCLKCFG reset value. SYSCLKCFGRST defines the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLKCFG
      </span>
     </span>
     output expected to be used for clock divider or generation configuration of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSCLK
      </span>
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     AONCLKCFGRST[3:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
     &ndash;
     <span class="documents-g.number.hex">
      0xF
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CLK_CFG1.AONCLKCFG reset value. AONCLKCFGRST defines the
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AONCLKCFG
      </span>
     </span>
     output expected to be used for clock divider or generation configuration of
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       AONCLK
      </span>
     </span>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;RSTREQENRST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;RSTREQEN reset value. CPU&lt;n&gt;RSTREQENRST defines the reset value of RESET_MASK.CPU&lt;n&gt;RSTREQEN that is used to mask the system reset request signal, often with the signal name
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       SYSRESETREQ
      </span>
     </span>
     , from CPU &lt;n&gt;. When set to &lsquo;0&rsquo; at reset, CPU&lt;n&gt; is not able to cause a system warm reset when setting its local AIRCR.SYSRESETREQ control in its Application Interrupt and Reset Control Register (AIRCR). Setting this to &lsquo;1&rsquo; allows the reset to be requested.
    </p>
    <p>
     This control must be set to &lsquo;0&rsquo; when HASCRYPTO = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     HASCPU&lt;n&gt;CPIF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0, 1
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     It specifies whether the coprocessor interface is included for CPU&lt;n&gt;:
    </p>
    <ul>
     <li>
      <p>
       1: Coprocessor interface is not included
      </p>
     </li>
     <li>
      <p>
       2: Coprocessor interface is included
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SOCIMPLID[11:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the SoC integrator.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The SoC integrator JEP106 code.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SOCREV[3:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the SoC integrator.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The SoC minor revision code.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SOCVAR[3:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the SoC integrator.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The SoC variant or major revision code.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SOCPRTID[11:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the SoC integrator.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The SoC product identity code.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPLID[11:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the implementor.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The subsystem implementor JEP106 code.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPLREV[3:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the implementor.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The subsystem minor revision code.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPLVAR[3:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the implementor.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The subsystem variant or major revision code.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPLPRTID[11:0]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the implementor.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The subsystem product identity code.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;MCUROMADDR[31:12]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     It is defined by the SoC integrator.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The address pointer to MCU ROM table private to each CPU core. Only the 20 most significant bits are configurable. All lower address bits are zeros. This configuration point must exist when HASCSS = 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CPU&lt;n&gt;MCUROMVALID
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     It is defined by the SoC integrator.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The address pointer to MCU ROM table private to each CPU core is valid. This configuration point must exist when HASCSS = 1.
    </p>
   </td>
  </tr>
 </tbody>
</table>
