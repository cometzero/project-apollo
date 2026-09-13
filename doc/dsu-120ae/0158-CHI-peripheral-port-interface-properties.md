# CHI peripheral port interface properties

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/CHI-peripheral-port-interface-properties>

### CHI peripheral port interface properties

AMBA defines a set of CHI interface properties that the interconnect can provide. The CHI configured peripheral port of theDynamIQ Shared Unit-120AE (DSU-120AE) cluster only supports some of these interface properties.

The following table shows which of these properties the CHI-configured peripheral port supports, and if interconnect or system support is required. You must ensure that your system interconnect, where applicable, supports these properties.

<table id="rfx1660577285375__table_w4291ab1c11b1b3_w4292ab1c11b1_w4293ab1c11_w4294ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CHI peripheral port interface properties
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d276476e74" rowspan="1">
    CHI property
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d276476e77" rowspan="1">
    Supported by the
    <span class="documents-keyword">
     DSU-120AE
    </span>
    cluster
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d276476e83" rowspan="1">
    Interconnect support required
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Atomic_Transactions
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    The
    <span class="documents-keyword">
     DSU-120AE
    </span>
    cluster supports this property if BROADCASTATOMIC is HIGH.
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cache_Stash_Transactions
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Direct_Memory_Transfer
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Direct_Cache_Transfer
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Data_Poison
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span>
     Yes
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Data_Check
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CCF_Wrap_Order
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Enhanced_Features
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     The
     <span class="documents-keyword">
      DSU-120AE
     </span>
     cluster supports data return from SC state.
    </p>
    <p>
     The
     <span class="documents-keyword">
      DSU-120AE
     </span>
     cluster does not support input/output deallocation transactions, for example ReadOnceMakeInvalid (ROMI) and ReadOnceCleanInvalid (ROCI).
    </p>
    <p>
     The
     <span class="documents-keyword">
      DSU-120AE
     </span>
     cluster supports ReadNotSharedDirty transactions and requires interconnect support.
    </p>
    <p>
     If
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       BROADCASTPERSIST
      </span>
     </span>
     is HIGH, the
     <span class="documents-keyword">
      DSU-120AE
     </span>
     cluster supports CleanSharedPersist transactions and requires interconnect support.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes, if the cluster supports ReadNotSharedDirty transactions or if the
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTPERSIST
     </span>
    </span>
    signal is set to HIGH.
   </td>
  </tr>
 </tbody>
</table>

The following table shows the different width values that the CHI-configured peripheral port supports.

<table id="rfx1660577285375__table_fds_fmd_ckb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Supported widths for CHI-configured peripheral port
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d276476e248" rowspan="1">
    Width
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d276476e251" rowspan="1">
    Value
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Req_Addr_Width
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The maximum width is 52 bits
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NodeID_Width
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The maximum width is 11 bits
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Data_Width
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The maximum width is 256 bits
   </td>
  </tr>
 </tbody>
</table>
