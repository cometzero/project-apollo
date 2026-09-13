# Configure CHI bus requester ports to use address target groups

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/Configure-CHI-bus-requester-ports-to-use-address-target-groups>

### Configure CHI bus requester ports to use address target groups

Configuring requester ports to use address target groups involves a three-step process. After configuring the number of bus requester ports required, the hashing for the address target groups must be defined. Finally, you must set the REQUESTERDISABLE signal to define the mapping between the address target groups and the bus requester ports.

### About this task

### Procedure

1. Configure the DynamIQ Shared Unit-120AE (DSU-120AE) for the number of bus requester ports required.

   Use the build time configuration parameter,
   `NUM_REQUESTERS` to specify the number of bus
   requester ports. See
   Configuring the RTL chapter in the
   Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual on how to configure the RTL for the
   DSU-120AE.
2. Set up the address hashing for the number of the address target groups required. For hashing algorithms, see [Hashing for CHI transaction distribution](/documentation/107721/0001/CHI-requester-interface/Configure-CHI-bus-requester-ports-to-use-address-target-groups/Hashing-for-CHI-transaction-distribution?lang=en "When more than one bus requester port is implemented, the hashing to decide which transaction goes to which address target group is based on the Physical Address (PA) of the transaction, and the number of requester ports configured. There is a 1-bit, 2-bit, or 3-bit value that is used to identify the address target group number for each transaction depending on the number of bus requester ports configured. This gives a maximum of eight groups.").

   The number of address target groups defined depends on the number of bus requester ports that have been configured at build time, as shown in the following table.

<table id="ons1660577263627__table_pqy_wry_jrb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Combinations of
   <span class="documents-keyword">
    requesters
   </span>
   and
   <span>
    <span class="documents-keyword">
     address target groups
    </span>
   </span>
   supported
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d262502e200" rowspan="1">
    Number of bus
    <span class="documents-keyword">
     requester
    </span>
    ports configured at build time
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d262502e206" rowspan="1">
    Number of
    <span>
     <span class="documents-keyword">
      address target groups
     </span>
    </span>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    6
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    8
   </td>
  </tr>
 </tbody>
</table>

3. Set the REQUESTERDISABLE signal, to define the mapping between the address target groups to the bus requester ports. For the table of address target group mappings, see [Mapping for address target groups to CHI bus requester ports](/documentation/107721/0001/CHI-requester-interface/Configure-CHI-bus-requester-ports-to-use-address-target-groups/Mapping-for-address-target-groups-to-CHI-bus-requester-ports?lang=en "The mapping between the address target groups and the bus requester ports is determined by which bus requester ports are disabled at reset time. This is done by setting the signal REQUESTERDISABLE[CMP-1:0], where CMP is the number of bus requester ports configured.").

   Once the mapping has been set up, the
   DSU-120AE automatically sets the id in the transaction address based on the allocation of the
   address target group numbers, see
   [CHI id bit setting](/documentation/107721/0001/CHI-requester-interface/Configure-CHI-bus-requester-ports-to-use-address-target-groups/CHI-id-bit-setting?lang=en "The allocation of address target groups numbers is also used to set the id, by the DynamIQ Shared Unit-120AE (DSU-120AE), in the transaction address.").
