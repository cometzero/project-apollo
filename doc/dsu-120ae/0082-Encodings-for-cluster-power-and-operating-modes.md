# Encodings for cluster power and operating modes

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Cluster-PPU-mode-control/Encodings-for-cluster-power-and-operating-modes>

### Encodings for cluster power and operating modes

The Power Policy Unit (PPU) registers, for example PPU\_PWPR, use power mode and operating mode encodings to set various conditions. For example, register bitfields PPU\_PWPR.PWR\_POLICY and PPU\_PWPR.OP\_POLICY require these values.

The following table shows the power mode encodings for the DSU-120AE DynamIQ™ cluster.

> ### Note
>
> In the following table:
>
> - PCSMPSTATE[3:0] refers to CLUSTERPCSMPSTATE[3:0]
> - PPUHWSTAT[15:0] refers to CLUSTERPPUHWSTAT[15:0]

<table id="gbe1660577250310__table_wqt_jf4_53b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Power mode enumeration for the DynamIQ cluster
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d46183e95" rowspan="1">
    Power mode
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e98" rowspan="1">
    PPU_PWPR.PWR_POLICY
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e101" rowspan="1">
    PCSMPSTATE[3:0]
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e104" rowspan="1">
    PPUHWSTAT[15:0]
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OFF
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0001
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OFF_EMU
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0002
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MEM_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0004
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MEM_RET_EMU
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0008
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FULL_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0020
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    FUNC_RET
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x7
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x7
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0080
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ON
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0100
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WARM_RST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x9
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0200
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DBG_RECOV
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xA
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0400
    </span>
   </td>
  </tr>
 </tbody>
</table>

The following table shows the DSU-120AE DynamIQ™ cluster operating mode encodings for PPU\_PWPR.OP\_POLICY bit field.

<table id="gbe1660577250310__table_cluster_opmode1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Operating mode encodings for PPU_PWPR.OP_POLICY bit field
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d46183e308" rowspan="2">
    Active slices
   </th>
   <th class="documents-cellrowborder" colspan="3" id="d46183e311" rowspan="1">
    Active RAMs
   </th>
  </tr>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d46183e317" rowspan="1">
    Snoop Filter Only (SFONLY)
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e320" rowspan="1">
    HALF RAM
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e323" rowspan="1">
    FULL RAM
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x9
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xB
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x7
    </span>
   </td>
  </tr>
 </tbody>
</table>

The following table shows the DSU-120AE DynamIQ™ cluster operating mode encodings for CLUSTERPCSMPSTATE[7:4] and CLUSTERPPUHWSTAT[31:16].

> ### Note
>
> In the following table:
>
> - PCSMPSTATE[7:4] refers to CLUSTERPCSMPSTATE[7:4]
> - PPUHWSTAT[31:16] refers to CLUSTERPPUHWSTAT[31:16]
> - For ALL\_SLICES, there are pairs of values of PCSMPSTATE[7:4] that are equivalent. There is no significance in meaning between each of the two different encodings. In some situations, the DSU-120AE might generate PCSM transition requests between equivalent encodings.

<table id="gbe1660577250310__table_cluster_opmode2">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   Operating mode enumeration for the
   <span class="documents-keyword">
    DSU-120AE
   </span>
   cluster
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d46183e455" rowspan="1">
    Operating mode name
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e458" rowspan="1">
    PPU_PWPR.OP_POLICY
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e461" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      PCSMPSTATE[7:4]
     </span>
    </span>
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e465" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      PPUHWSTAT[31:16]
     </span>
    </span>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE, SFONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x01
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE, HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x02
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE, FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x08
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES, SFONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x100
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES, HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x9
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x9
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x200
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES, FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xB
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xB
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x800
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES, SFONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    or
    <span class="documents-g.number.hex">
     0x
     <span>
      C
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x10
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES, HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
    or
    <span class="documents-g.number.hex">
     0x
     <span>
      D
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x20
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES, FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x7
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x7
    </span>
    or
    <span class="documents-g.number.hex">
     0x
     <span>
      F
     </span>
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x80
    </span>
   </td>
  </tr>
 </tbody>
</table>

The following table shows for each operating mode which L3 memory system variants are supported.

<table id="gbe1660577250310__table_ngf_kmf_cvb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 4.
   </span>
   Supported operating modes for different L3 memory system variants
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d46183e672" rowspan="1">
    Operating mode name
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e675" rowspan="1">
    PPU_PWPR.OP_POLICY
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d46183e678" rowspan="1">
    Default configuration (with L3 cache and SCU)
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE, SFONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="9">
    Supported
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE, HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ONE SLICE, FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES, SFONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x8
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES, HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x9
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    HALF SLICES, FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xB
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES, SFONLY
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES, HALF RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ALL SLICES, FULL RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x7
    </span>
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> When programming the OP\_POLICY field in static mode, ensure that the new value is a single valid transition from the current value, otherwise the request will be denied. Changing the slice bits and the RAM bits at the same time might also be denied.
>
> When using dynamic mode, Arm recommends that you set the the OP\_POLICY field to 0 and use the CLUSTERPWRCTLR register to request changes to the operating mode. Setting OP\_POLICY to any other value might prevent transitions to some operating modes even if they are considered higher than the programmed value.
