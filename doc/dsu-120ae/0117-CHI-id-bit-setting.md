# CHI id bit setting

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/Configure-CHI-bus-requester-ports-to-use-address-target-groups/CHI-id-bit-setting>

### CHI id bit setting

The allocation of address target groups numbers is also used to set the id, by the DynamIQ Shared Unit-120AE (DSU-120AE), in the transaction address.

The following table shows how the address target id of the transaction, TgtID, is set depending on what address target group the transaction has been assigned.

<table id="sla1660577264920__table_hhr_3ns_lrb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Address target ID value dependency on
   <span>
    <span class="documents-keyword">
     address target groups
    </span>
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
   <th class="documents-cellrowborder" colspan="1" id="d34117e81" rowspan="1">
    Number of groups
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d34117e84" rowspan="1">
    TgtID = 0
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d34117e87" rowspan="1">
    TgtID = 1
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Group 0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Group 1
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Groups 0, 1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Groups 2, 3
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    6
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Groups 0, 1, 2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Groups 3, 4, 5
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    8
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Groups 0, 1, 2, 3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Groups 4, 5, 6, 7
   </td>
  </tr>
 </tbody>
</table>
