# Utility bus accesses

Source: <https://developer.arm.com/documentation/107721/0001/Utility-bus/Utility-bus-accesses>

### Utility bus accesses

Transactions on the utility bus comply with a subset of the AXI5 bus protocol. Access sizes must be either 32-bits or 64-bits. Any other sized access generates a SLVERR response from the utility bus.

You must observe the following requirements when accessing the utility bus:

- Only ReadNoSnoop and WriteNoSnoop transaction types are supported.
- Only 32-bit accesses or 64-bit accesses are supported. Therefore, ARSIZEU or AWSIZEU must be either 0b010 for 32-bit sized accesses, or 0b011 for 64-bit sized accesses. Any other access size generates a SLVERR response from the utility bus.
- Only single beat bursts are supported. Therefore, ARLENU or AWLENU must be 0b00000000. Any other burst length generates a SLVERR response from the utility bus.
- Some of the system components control registers only support Secure state or Root state accesses on the utility bus, see [Utility bus base addresses for system-accessible component registers](/documentation/107721/0001/Utility-bus/Base-addresses-for-system-accessible-components?lang=en#ryl1660577298593__table_system_components_util_bus_ae). Ensure that you access any system component register with the security set appropriately. Any register in the wrong security state is treated as RAZ/WI.

Arm® recommends the following, when accessing the utility bus:

- ARCACHEU or AWCACHEU is either 0b0000 or 0b0001, although other values are accepted.
- ARBURSTU or AWBURSTU is 0b01, although other values are accepted.
- ARLOCKU or AWLOCKU is tied LOW, as there is no exclusive monitor present.

The following table describes the utility bus acceptance capabilities:

<table id="zrq1660577296744__table_rnh_dbd_vlb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Utility bus acceptance capabilities
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d283473e154" rowspan="1">
    Attribute
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d283473e157" rowspan="1">
    Value
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d283473e160" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Write acceptance capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The utility bus can accept 1 write transaction.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Read acceptance capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The utility bus can accept 1 read transaction.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Combined acceptance capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The utility bus can accept up to 2 transactions.
   </td>
  </tr>
 </tbody>
</table>
