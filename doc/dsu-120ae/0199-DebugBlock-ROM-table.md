# DebugBlock ROM table

Source: <https://developer.arm.com/documentation/107721/0001/ROM-tables/DebugBlock-ROM-table>

### DebugBlock ROM table

The DebugBlock ROM table contents depends on how you configured your cluster.

The following table lists the entries for the DebugBlock ROM table, together with associated offsets from the physical base address of the ROM table. The DebugBlock ROM table includes:

- All the debug components for DebugBlock including the Cross Trigger Interfaces (CTIs) for each core.
- Entry point for the cluster ROM table
- Power control register to allow a cluster powerup request, see [ROM table power request registers for cluster and cores](/documentation/107721/0001/ROM-tables/ROM-table-power-request-registers-for-cluster-and-cores?lang=en "Your debugger can program up the appropriate Debug Power Control Registers to request a powerup for the cluster, cores, or complexes from the corresponding Power Policy Unit (PPU).").

The ROMENTRY entry values depend on the number and type of cores implemented. The register formats are described in the [Arm® CoreSight™ Architecture Specification v3.0](https://developer.arm.com/documentation/ihi0029/latest).

> ### Note
>
> The DebugBlock ROM table part number is
> 0x4E9.

<table id="alq1660577311318__table_wkl_sfz_zv">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DebugBlock ROM table
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d99060e129" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d99060e132" rowspan="1">
    Name
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d99060e135" rowspan="1">
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
    Cluster ROM table entry point
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
    Cluster CTI
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    0
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    1
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    2
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    3
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    4
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    5
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    6
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    7
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    8
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    9
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    10
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    11
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    12
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
    CTI for
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    13
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0048
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
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DBGPCR0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Debug Power Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0A04
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
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DBGPSR0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Debug Power Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0A84
    </span>
    -
    <span class="documents-g.number.hex">
     0x0AFC
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
     0x0B00
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SYSPCR0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    System Power Control Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0B04
    </span>
    -
    <span class="documents-g.number.hex">
     0x0B7C
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
     0x0B80
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SYSPSR0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    System Power Status Register
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0B84
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
     0x0C04
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
    <p>
     <span class="documents-g.number.hex">
      0x0FCC
     </span>
    </p>
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
    <p>
     Peripheral Identification Register 4
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0FD4
    </span>
    -0FDC
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
