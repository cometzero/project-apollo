# CHI features

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/CHI-features>

### CHI features

AMBA defines a set of interface properties for the Coherent Hub Interface (CHI) interconnect. You must ensure that your system interconnect, where applicable, supports these properties.

The following table shows which of these properties the DynamIQ Shared Unit-120AE (DSU-120AE) supports, or requires the interconnect and system to support.

<table id="gpn1660577266232__table_w422ab1c11b1b3_w423ab1c11b1_w424ab1c11_w425ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CHI interconnect properties for the
   <span class="documents-keyword">
    DSU-120AE
   </span>
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d255831e79" rowspan="1">
    CHI property
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d255831e82" rowspan="1">
    Supported by the
    <span class="documents-keyword">
     DSU-120AE
    </span>
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d255831e87" rowspan="1">
    Interconnect support required
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Atomic_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes if
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTATOMIC
     </span>
    </span>
    is HIGH.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes if
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTATOMIC
     </span>
    </span>
    is HIGH.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cache_Stash_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Direct_Memory_Transfer
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OPTIONAL. The
    <span class="documents-keyword">
     DSU-120AE
    </span>
    supports this feature if required by your interconnect.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Direct_Cache_Transfer
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    OPTIONAL. The
    <span class="documents-keyword">
     DSU-120AE
    </span>
    supports this feature if required by your interconnect.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Data_Poison
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Yes
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Data_Check
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    CCF_Wrap_Order
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No. The
    <span class="documents-keyword">
     DSU-120AE
    </span>
    sends data packets in any order.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Barrier_Transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No. The
    <span class="documents-keyword">
     DSU-120AE
    </span>
    does not use these transaction types.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Data return from SC state
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Not applicable
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    I/O de-allocation transactions (ROMI and ROCI)
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    No. The
    <span class="documents-keyword">
     DSU-120AE
    </span>
    does not use these transaction types.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ReadNotSharedDirty transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    CleanSharedPersist transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes if
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTPERSIST
     </span>
    </span>
    is HIGH.
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes if
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTPERSIST
     </span>
    </span>
    is HIGH.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    DVM_v8.4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes if any of the signals
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTICINVAL
     </span>
    </span>
    ,
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTTLBIINNER
     </span>
    </span>
    or
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTTLBIOUTER
     </span>
    </span>
    is HIGH.
   </td>
  </tr>
 </tbody>
</table>

The following table shows the values for the CHI requester interface values for the DSU-120AE.

<table id="gpn1660577266232__table_pnt_5xy_1jb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   CHI
   <span class="documents-keyword">
    requester
   </span>
   interface values for the
   <span class="documents-keyword">
    DSU-120AE
   </span>
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d255831e325" rowspan="1">
    CHI property
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d255831e328" rowspan="1">
    Value
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d255831e331" rowspan="1">
    Comment
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Req_Addr_Width
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    52
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     If the cluster only contains
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     that have a Physical Address (PA) width which is 48 bits or smaller, then this value is 48.
    </p>
    <p>
     If the cluster only contains
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     that have a PA width which are 44 bits or smaller, then this value is 44.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NodeID_Width
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    11
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Data_Width
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    256 bits
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
 </tbody>
</table>

For more information on these features, see the  [AMBA® CHI Architecture Specification](https://developer.arm.com/documentation/ihi0050/latest/).

> ### Note
>
> The DSU-120AE does not use the Streaming Ordered Writes feature of CHI. This means that for WriteNoSnp and WriteUnique transactions, the DSU never uses the combination of Order 0b10 and ExpCompAck HIGH.
