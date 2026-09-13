# Cluster ROM table

Source: <https://developer.arm.com/documentation/107721/0001/ROM-tables/Cluster-ROM-table>

### Cluster ROM table

The cluster ROM table contents depends on how you configured your cluster.

The following table lists the entries for the cluster ROM table, together with associated offsets from the physical base address of the ROM table. The cluster ROM table includes:

- All the debug components present at the cluster-level including the cluster Performance Monitoring Unit (PMU) and the cluster Embedded Logic Analyzer (ELA).
- Entry points to the ROM tables for each standalone core or complex
- Power control registers for each standalone core or complex to allow core or complex powerup requests, see [ROM table power request registers for cluster and cores](/documentation/107721/0001/ROM-tables/ROM-table-power-request-registers-for-cluster-and-cores?lang=en "Your debugger can program up the appropriate Debug Power Control Registers to request a powerup for the cluster, cores, or complexes from the corresponding Power Policy Unit (PPU).").

The ROMENTRY entry values depend on the number and type of cores implemented. The register formats are described in the [Arm® CoreSight™ Architecture Specification v3.0](https://developer.arm.com/documentation/ihi0029/latest).

> ### Note
>
> - If a complex of two cores is present, then each complex gets a single ROMENTRY that covers all cores in the complex. Therefore, where the table states Core, for example in the entry Core 0 ROM table, this can either be a core, a single-core complex, or a dual-core complex.
> - In the following table, n corresponds to the ROMENTRY number for either the core or cluster.
> - The cluster ROM table part number is 0x4EA.

<table id="ffy1660577311831__table_wkl_sfz_zv">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   ROM table registers
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d128477e188" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d128477e191" rowspan="1">
    Name
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d128477e194" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0000
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster PMU
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0004
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY1
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Cluster ELA
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0008
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY2
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 0 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x000C
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY3
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 1 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0010
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY4
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 2 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0014
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY5
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 3 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0018
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY6
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 4 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x001C
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY7
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 5 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0020
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY8
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 6 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0024
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY9
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 7 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0028
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY10
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 8 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x002C
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY11
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 9 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0030
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY12
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 10 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0034
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY13
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 11 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0038
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY14
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 12 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x003C
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ROMENTRY15
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Core 13 ROM table
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0040
    </span>
    -
    <span class="documents-g.number.hex">
     0x09FC
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0A00
    </span>
    -
    <span class="documents-g.number.hex">
     0x0A34
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DBGPCR&lt;n&gt;
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Debug Power Control Register for core &lt;n&gt;
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0A38
    </span>
    -
    <span class="documents-g.number.hex">
     0x0A7C
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0A80
    </span>
    -
    <span class="documents-g.number.hex">
     0x0AB4
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DBGPSR&lt;n&gt;
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Debug Power Status Register for core &lt;n&gt;
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0AB8
    </span>
    -
    <span class="documents-g.number.hex">
     0x0BFC
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0C00
    </span>
    -
    <span class="documents-g.number.hex">
     0x0C1C
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PRIDR0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Power Reset Identification Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0C20
    </span>
    -
    <span class="documents-g.number.hex">
     0x0FB4
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FB8
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AUTHSTATUS
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Authentication Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FBC
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DEVARCH
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device Architecture Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FC0
    </span>
    -
    <span class="documents-g.number.hex">
     0x0FC4
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FC8
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DEVID
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device ID Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FCC
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DEVTYPE
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Device Type Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FD0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PIDR4
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 4
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FD4
    </span>
    -
    <span class="documents-g.number.hex">
     0x0FDC
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FE0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PIDR0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FE4
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PIDR1
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FE8
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PIDR2
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FEC
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PIDR3
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Peripheral Identification Register 3
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FF0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CIDR0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Component Identification Register 0
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FF4
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CIDR1
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Component Identification Register 1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FF8
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CIDR2
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Component Identification Register 2
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FFC
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CIDR3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Component Identification Register 3
   </td>
  </tr>
 </tbody>
</table>
