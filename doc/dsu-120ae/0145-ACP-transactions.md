# ACP transactions

Source: <https://developer.arm.com/documentation/107721/0001/ACP-subordinate-interface/ACP-transactions>

### ACP transactions

The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification. The ACP interface includes support for Cacheable, Non-cacheable, Device, and Atomic memory accesses.

The following table lists the subset of the ACE-LiteDVM transaction types that are supported in the ACP interface.

<table id="rrs1660577278758__table_myt_k5k_4jb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   ACP supported transaction types
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d25684e67" rowspan="1">
    Transaction group
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d25684e70" rowspan="1">
    Transaction type
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="2">
    Read
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ReadOnce
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ReadNoSnoop
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="4">
    Write
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WriteUniquePtl
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WriteUniqueFull
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WriteUniquePtlStash
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    WriteNoSnoop
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="2">
    Dataless
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    StashOnceUnique
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    StashOnceShared
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="4">
    Atomic
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    AtomicStore
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    AtomicLoad
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    AtomicSwap
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    AtomicCompare
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> The transaction types WriteUniqueFull and WriteUniquePtl in the AMBA ACE5-LiteDVM specification are known in the AMBA 4 ACE­Lite specification as WriteLineUnique and WriteUnique, respectively.

The following table shows the attributes for read transactions types for 128-bit (16-byte) data width mode.

<table id="rrs1660577278758__table_ggw_5lc_4jb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Attributes for read transaction types for 128-bit data width mode
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
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e196" rowspan="2">
    Read request type
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e199" rowspan="2">
    ARSIZE
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e202" rowspan="2">
    ARLEN
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e205" rowspan="2">
    ARBURST
   </th>
   <th class="documents-cell-norowborder" colspan="2" id="d25684e208" rowspan="1">
    Address alignment
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e214" rowspan="1">
    INCR
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d25684e217" rowspan="1">
    WRAP
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    (16-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
    (4-beats)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[5:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    (16-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
    (2-beats)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[4:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    (16-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
    (8-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[2:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    8-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[2:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2
    </span>
    (4-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[1:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    4-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[1:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
    (2-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    2-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    1-byte
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-byte)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Any
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Any
   </td>
  </tr>
 </tbody>
</table>

The following table shows the attributes for read transactions types for 256-bit (32-byte) data width mode.

<table id="rrs1660577278758__table_owf_qx3_xjb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   Attributes for read transaction types for 256-bit data width mode
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
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e510" rowspan="2">
    Read request type
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e513" rowspan="2">
    ARSIZE
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e516" rowspan="2">
    ARLEN
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e519" rowspan="2">
    ARBURST
   </th>
   <th class="documents-cell-norowborder" colspan="2" id="d25684e522" rowspan="1">
    Address alignment
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e528" rowspan="1">
    INCR
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d25684e531" rowspan="1">
    WRAP
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
    (32-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
    (2-beats)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[5:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    32-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[4:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00000
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
    (32-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beats)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[4:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    32-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[4:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00000
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    (16-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
    (8-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[2:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    8-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[2:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2
    </span>
    (4-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[1:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    4-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[1:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
    (2-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    2-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      ARADDR[0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0
    </span>
    )
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    1-byte
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-byte)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Any
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Any
   </td>
  </tr>
 </tbody>
</table>

The following table shows the attributes for write transactions types for 128-bit (16-byte) data width mode.

<table id="rrs1660577278758__table_yzc_dgj_4jb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 4.
   </span>
   Attributes for write transaction types for 128-bit data width mode
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
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e825" rowspan="2">
    Write request type
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e828" rowspan="2">
    AWSIZE
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e831" rowspan="2">
    AWLEN
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e834" rowspan="2">
    AWBURST
   </th>
   <th class="documents-nocellnorowborder" colspan="2" id="d25684e837" rowspan="1">
    Address alignment
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d25684e841" rowspan="2">
    Comment
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e847" rowspan="1">
    INCR
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d25684e850" rowspan="1">
    WRAP
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    (16-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
    (4-beats)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[5:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000000
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    If
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWSNOOP
     </span>
    </span>
    is WriteUniquePtl, then any combination of bytes is valid. If
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWSNOOP
     </span>
    </span>
    is WriteUniqueFull, then all bytes must be valid.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    (16-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
    (2-beats)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[4:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00000
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    (16-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid. This includes no bytes, which mimics a
    <code>
     PLDW
    </code>
    instruction (read-unique preload).
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
    (8-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[2:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[2:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2
    </span>
    (4-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[1:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[1:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
    (2-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    1-byte
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-byte)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Any
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Any
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
 </tbody>
</table>

The following table shows the attributes for write transactions types for 256-bit (32-byte) data width mode.

<table id="rrs1660577278758__table_i3f_px3_xjb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 5.
   </span>
   Attributes for write transaction types for 256-bit data width mode
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
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e1174" rowspan="2">
    Write request type
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e1177" rowspan="2">
    AWSIZE
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e1180" rowspan="2">
    AWLEN
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e1183" rowspan="2">
    AWBURST
   </th>
   <th class="documents-nocellnorowborder" colspan="2" id="d25684e1186" rowspan="1">
    Address alignment
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d25684e1190" rowspan="2">
    Comment
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d25684e1196" rowspan="1">
    INCR
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d25684e1199" rowspan="1">
    WRAP
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
    (32-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
    (2-beats)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    64-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[5:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000000
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[4:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    If
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWSNOOP
     </span>
    </span>
    is WriteUniquePtl, then any combination of bytes is valid. If
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWSNOOP
     </span>
    </span>
    is WriteUniqueFull, then all bytes must be valid.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x5
    </span>
    (32-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[4:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00000
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    32-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[4:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x4
    </span>
    (16-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    16-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[3:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid. This includes no bytes, which mimics a
    <code>
     PLDW
    </code>
    instruction (read-unique preload).
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x3
    </span>
    (8-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[2:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    8-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[2:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b000
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x2
    </span>
    (4-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[1:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    4-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[1:0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b00
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x1
    </span>
    (2-bytes)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0
    </span>
    )
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    2-byte boundary (
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      AWADDR[0]
     </span>
    </span>
    =
    <span class="documents-g.number.bin">
     0b0
    </span>
    )
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    1-byte
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-byte)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
    (1-beat)
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    INCR or WRAP
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Any
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Any
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Any combination of bytes is valid.
   </td>
  </tr>
 </tbody>
</table>

Stash requests can target the L2 cache of a selected core by asserting signal AWSTASHLPIDENS and indicating the selected core instance number on AWSTASHLPIDS[3:0]. See [Core, complex, and processing element numbering](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Core--complex--and-processing-element-numbering?lang=en "A cluster contains two or more cores. The cluster can also contain two or more complexes which can be made up of either a single core or two cores. Because certain parts of the design, such as signal names and register bit values, depend on the number of cores and complexes within the cluster, a numbering system has been created.") for a description of the core instance number.

All ACE5-LiteDVM signals are present on the ACP interface, except AxLOCK and AxQOS. For the unconnected signal AxLOCK, the ACP interface does not support exclusives and therefore the functionality matches the AxLOCK signal being tied LOW.

> ### Note
>
> The DSU-120AE generates an SLVERRn in response to any of the following conditions:
>
> - AxDOMAIN is 0b11 (System domain access) when AxCACHE is 0bxx11 (Write-Back cacheable).
> - For 128-bit wide data mode, AxLEN is a value other than 0b00000011, 0b00000001, or 0b00000000.
> - For 256-bit wide data mode, AxLEN is a value other than 0b00000001 or 0b00000000.
> - For 128-bit wide data mode, an SLVERR is produced if either:
>   - AxLEN is 00000001 and AxADDR[4:0] is a value other than 0b00000.
>   - AxLEN is 00000011 and AxADDR[5:0] is a value other than 0b000000.
> - For 256-bit wide data mode, AxADDR[5:0] is a value other than 0b000000 when AxLEN is not 0b00000000.
> - AWSNOOP is any transaction other than WriteNoSnoop, WriteUniquePtl, WriteUniqueFull, WriteUniquePtlStash, WriteUniqueFullStash, StashOnceShared, StashOnceUnique, AtomicLoad, AtomicStore, AtomicSwap, or AtomicCompare.
> - ARSNOOP is any transaction other than ReadNoSnoop, ReadOnce, or DVMComplete.
> - AxBURST is a value other than 0b01 or 0b10. Only incremental or wrap bursts are supported.

Values of AxCACHE that are not fully supported are mapped to the nearest supported memory type that has the same or stronger requirements.
