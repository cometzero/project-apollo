# Encodings for core power modes

Source: <https://developer.arm.com/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Core-power-mode-control/Encodings-for-core-power-modes>

### Encodings for core power modes

The core Power Policy Unit (PPU) register bitfield PPU\_PWPR.PWR\_POLICY encodes the supported power modes for the cores.

The following table shows the encodings for the core power modes.

> ### Note
>
> In the following table:
>
> - PCSMPSTATE[3:0] refers to CORE<CN>PCSMPSTATE[3:0], where CN is the core instance number
> - PPUHWSTAT[15:0] refers to CORE<CN>PPUHWSTAT[15:0], where CN is the core instance number

<table id="mdc1660577251827__table_wqt_jf4_53b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Power mode enumeration for the
   <span>
    <span class="documents-keyword">
     cores
    </span>
   </span>
   in the
   <span>
    <span class="documents-keyword">
     DSU-120AE DynamIQ&trade; cluster
    </span>
   </span>
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
   <th class="documents-cellrowborder" colspan="1" id="d355980e116" rowspan="1">
    Power mode
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d355980e119" rowspan="1">
    PPU_PWPR.PWR_POLICY
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d355980e122" rowspan="1">
    PCSMPSTATE[3:0]
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d355980e125" rowspan="1">
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

The CORE<CN>PCSMSTATE[15:4] value is 0x000.

For information on the PPU registers, see [External cluster PPU registers](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Cluster-PPU-mode-control/External-cluster-PPU-registers?lang=en "The Power Policy Unit (PPU) registers for the DSU-120AE DynamIQ cluster are only accessible from memory-mapped accesses on the utility bus.") and [External core PPU registers](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units/Core-power-mode-control/External-core-PPU-registers?lang=en "Each core Power Policy Unit (PPU) in the DSU-120AE DynamIQ cluster has an individual set of Power Policy Unit (PPU) registers. Each set of registers is identical, and are memory-mapped onto the utility bus at different base addresses.").

### Related information

- [Core, complex, and processing element numbering](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Core--complex--and-processing-element-numbering?lang=en "A cluster contains two or more cores. The cluster can also contain two or more complexes which can be made up of either a single core or two cores. Because certain parts of the design, such as signal names and register bit values, depend on the number of cores and complexes within the cluster, a numbering system has been created.")
