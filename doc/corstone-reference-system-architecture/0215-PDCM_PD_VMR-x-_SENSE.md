# PDCM_PD_VMR<x>_SENSE

Source: <https://developer.arm.com/documentation/102803/latest/Programmers-model/System-Control-Peripheral-Region/System-Control-Register-Block/PDCM-PD-VMR-x--SENSE>

### PDCM\_PD\_VMR<x>\_SENSE

The Power Dependency Control Matrix Volatile Memory Region <x> Power domain (PD\_VMR<x>) Sensitivity register is used to define what keeps awake the PD\_VMR<x> domain and the minimum power state to use when the domain is in its low power state, where x is 0 to NUMVMBANK-1.

### Configurations

This register implementation depends on the configuration of individual fields. When PILEVEL < 1, these registers do not exist and the register areas they occupy are Reserved, and RAZ/WI.

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
   PDCM_PD_VMR&lt;x&gt;_SENSE bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d99669e113" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d99669e117" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d99669e121" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d99669e125" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d99669e129" rowspan="1">
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
     31:30
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     MIN_PWR_STATE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Defines the Minimum Power State, when PD_VMR&lt;x&gt; is trying to enter a lower power state:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;00&rsquo;: Minimum power state is OFF,
      </p>
     </li>
     <li>
      <p>
       &lsquo;01&rsquo;: Minimum power state is Retention,
      </p>
     </li>
     <li>
      <p>
       &lsquo;10&rsquo;: Minimum power state is ON,
      </p>
     </li>
     <li>
      <p>
       Others: Reserved.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     29:24
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
      0x0
     </span>
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
     S_PDCMRETQREQ3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable sensitivity to
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMRETQREQn[3]
      </span>
     </span>
     signal. If set to &lsquo;1&rsquo;,, PD_VMR&lt;x&gt; stay in ON or RET if
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMRETQREQn[3]
      </span>
     </span>
     signal is HIGH. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PDCMQCHWIDTH &lt; 4.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PDCMRETQREQ2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable sensitivity to
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMRETQREQn[2]
      </span>
     </span>
     signal. If set to &lsquo;1&rsquo;, PD_ VMR&lt;x&gt; stays in ON or RET if
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMRETQREQn[2]
      </span>
     </span>
     signal is HIGH. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PDCMQCHWIDTH &lt; 3.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PDCMRETQREQ1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable sensitivity to
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMRETQREQn[1]
      </span>
     </span>
     signal. If set to &lsquo;1&rsquo;, PD_ VMR&lt;x&gt; stays in ON or RET if
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMRETQREQn[1]
      </span>
     </span>
     signal is HIGH. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PDCMQCHWIDTH &lt; 2.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PDCMRETQREQ0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable sensitivity to
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMQRETREQn[0]
      </span>
     </span>
     signal. If set to &lsquo;1&rsquo;, PD_ VMR&lt;x&gt; stays in ON or RET if [PDCMRETQREQn
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       0]
      </span>
     </span>
     signal is HIGH. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PDCMQCHWIDTH &lt; 1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PDCMONQREQ3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable sensitivity to [PDCMONQREQn
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       3
      </span>
     </span>
     signal. If set to &lsquo;1&rsquo;, D_VMR&lt;x&gt; stays ON if
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMONQREQn[3]
      </span>
     </span>
     signal is HIGH. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PDCMQCHWIDTH &lt; 4.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PDCMONQREQ2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable sensitivity to
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMONQREQn[2]
      </span>
     </span>
     signal. If set to &lsquo;1&rsquo;, PD_VMR&lt;x&gt; stays ON if
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMONQREQn[2]
      </span>
     </span>
     signal is HIGH. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PDCMQCHWIDTH &lt; 3.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PDCMONQREQ1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable sensitivity to
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMONQREQn[1]
      </span>
     </span>
     signal. If set to &lsquo;1&rsquo;, PD_VMR&lt;x&gt; stays ON if
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMONQREQn[1]
      </span>
     </span>
     signal is HIGH. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PDCMQCHWIDTH &lt; 2.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PDCMONQREQ0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable sensitivity to
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMONQREQn[0]
      </span>
     </span>
     signal. If set to &lsquo;1&rsquo;, PD_VMR&lt;x&gt; stays ON if
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       PDCMONQREQn[0]
      </span>
     </span>
     signal is HIGH. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PDCMQCHWIDTH &lt; 1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PD_MGMT_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Tied to LOW. Ignores PD_MGMT power state. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if PILEVEL &lt; 2.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
      0x0
     </span>
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
     S_PD_DEBUG_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Tied to LOW. Ignores PD_DEBUG power state.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PD_CRYPTO_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Tied to LOW. Ignores PD_CRYPTO power state. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if HASCRYPTO = 0.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     11:9
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
      0x000
     </span>
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
     S_PD_NPU3_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable PD_NPU3 sensitivity. If set to &lsquo;1&rsquo;, PD_ VMR&lt;x&gt; stays ON if PD_NPU3 is ON. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 4.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PD_NPU2_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable PD_NPU2 sensitivity. If set to &lsquo;1&rsquo;, PD_ VMR&lt;x&gt; stays ON if PD_NPU2 is ON. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 3.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PD_NPU1_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable PD_NPU1 sensitivity. If set to &lsquo;1&rsquo; PD_ VMR&lt;x&gt; stays ON if PD_NPU1 is ON. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 2.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PD_NPU0_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable PD_NPU0 sensitivity. If set to &lsquo;1&rsquo; PD_ VMR&lt;x&gt; stays ON if PD_NPU0 is ON. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMNPU &lt; 1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PD_CPU3_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable PD_CPU3 sensitivity. If set to &lsquo;1&rsquo;, PD_ VMR&lt;x&gt; stays ON if PD_CPU3 is ON. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 3.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PD_CPU2_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable PD_CPU2 sensitivity. If set to &lsquo;1&rsquo;, PD_ VMR&lt;x&gt; stays ON if PD_CPU2 is ON. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 2.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
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
     S_PD_CPU1_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable PD_CPU1 sensitivity. If set to &lsquo;1&rsquo; PD_ VMR&lt;x&gt; stays ON if PD_CPU1 is ON. This bit is reserved and
     <span class="documents-archterm">
      RAZ/WI
     </span>
     if NUMCPU &lt; 1.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
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
     S_PD_CPU0_ON
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable PD_CPU0 sensitivity. If set to &lsquo;1&rsquo; PD_ VMR&lt;x&gt; stays ON if PD_CPU0 is ON.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
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
     S_PD_SYS_ON
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Tied to LOW. Ignores PD_SYS power state.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
