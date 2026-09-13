# AXI transaction routing with multiple manager ports

Source: <https://developer.arm.com/documentation/107721/0001/AXI-manager-interface/AXI-transaction-routing-with-multiple-manager-ports>

### AXI transaction routing with multiple manager ports

Transactions from the cores are routed, using the address target groups, to one of the CHI bus manager ports based on the transaction type, memory type, and transaction address.

> ### Note
>
> Address target group[0] has special functionality. Depending on your configuration signals, Device transactions are assigned to address target group 0. Typically, address target group 0 is mapped to bus interface port 0, but there might be special circumstances where bus interface port 0 is disabled. See
> [Mapping between address target groups and bus manager ports](/documentation/107721/0001/AXI-manager-interface/Configure-AXI-bus-manager-ports-to-use-address-target-groups/Mapping-for-address-target-groups-to-AXI-bus-manager-ports?lang=en#gjx1660577271751__axi_table_mp_mapping) for details.

The following table summarizes how transactions are routed to based on the transaction type.

<table id="zsy1660577272640__table_chi_routing">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CHI transaction routing
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d177494e81" rowspan="1">
    Transaction type
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d177494e84" rowspan="1">
    Routed to
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cacheable transactions
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Bus
    <span class="documents-keyword">
     manager
    </span>
    port number that is based on the address target group.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Normal Non-cacheable transactions
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Bus
    <span class="documents-keyword">
     manager
    </span>
    port number that is based on the target address group.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Device non-reorderable transactions
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     These transactions are sent to either:
    </p>
    <ul id="zsy1660577272640__ul_f2m_cb2_lrb">
     <li>
      The bus
      <span class="documents-keyword">
       manager
      </span>
      port which is assigned to address target group 0.
     </li>
     <li>
      All bus
      <span class="documents-keyword">
       manager
      </span>
      interfaces.
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Device reorderable transactions
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Bus
    <span class="documents-keyword">
     manager
    </span>
    port number that is based on the target address group.
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> - In the preceding table, you can find the bus manager port that corresponds to the target group given from the look-up table, see [Mapping between address target groups and bus requester ports](/documentation/107721/0001/CHI-requester-interface/Configure-CHI-bus-requester-ports-to-use-address-target-groups/Mapping-for-address-target-groups-to-CHI-bus-requester-ports?lang=en#kft1660577264504__table_mp_mapping).
> - By default, transactions described in the preceding table are directed to one of the manager interface ports unless they match one of the peripheral port address ranges. However, if the DEFAULTP signal is asserted at reset, then the mapping is inverted. Therefore all transactions, go to the Peripheral port except those that match the configured address ranges. These transactions that match the configured address ranges are sent to the main manager interface ports instead.

Cacheable and Non-cacheable transactions
:   For Cacheable transactions and Normal Non-cacheable transactions, routing from the
    cores are based on the
    address target group of the transaction. A configurable hash of the transaction address selects which
    manager interface port is used. See
    [Hashing for AXI transaction distribution](/documentation/107721/0001/AXI-manager-interface/Configure-AXI-bus-manager-ports-to-use-address-target-groups/Hashing-for-AXI-transaction-distribution?lang=en "When more than one bus manager port is implemented, the hashing to decide which transaction goes to which address target group is based on the Physical Address (PA) of the transaction, and the number of manager ports configured. There is a 1-bit, 2-bit, or 3-bit value that is used to identify the address target group number for each transaction, depending on the number of bus manager ports configured. This gives a maximum of eight groups.").

Device non-reorderable transactions
:   Device non-reorderable transactions are either always routed to address target group 0 or are routed based on the calculated address target group and on the value of the DEVNRINTERLEAVE[1:0] input signal as follows:
:   0b00
    :   All Device non-reorderable transactions are sent to address target group 0.

    0b01
    :   Device non-reorderable transactions are sent to any manager interface port that is based on the same address interleaving as for non-Device transactions.

    0b10
    :   Reserved

    0b11
    :   There is no downstream convergence of traffic from different ports. This includes transactions sent on the same physical port using a different TgtID due to having a different address target group. This means that the system interconnect design must guarantee that the transactions from different ports or from the same port but with different TgtID values are not routed to the same endpoint and therefore the ReadReceipt or Data Buffer ID (DBID) is enough to guarantee global ordering.
