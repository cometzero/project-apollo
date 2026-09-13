# Mapping for address target groups to AXI bus manager ports

Source: <https://developer.arm.com/documentation/107721/0001/AXI-manager-interface/Configure-AXI-bus-manager-ports-to-use-address-target-groups/Mapping-for-address-target-groups-to-AXI-bus-manager-ports>

### Mapping for address target groups to AXI bus manager ports

The mapping between the address target groups and the bus manager ports is determined by which bus manager ports are disabled at reset time. This is done by setting the signal REQUESTERDISABLE[CMP-1:0], where CMP is the number of bus manager ports configured.

The following table shows the mapping between the address target groups (groups) and the bus manager ports, where MP is the bus manager port number.

<table id="gjx1660577271751__axi_table_mp_mapping">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Mapping between
   <span>
    <span class="documents-keyword">
     address target groups
    </span>
   </span>
   and bus
   <span class="documents-keyword">
    manager
   </span>
   ports
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d157801e106" rowspan="1">
    Number of bus
    <span class="documents-keyword">
     manager
    </span>
    ports (CMP)
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d157801e112" rowspan="1">
    <span>
     <span class="documents-keyword">
      REQUESTER
     </span>
     DISABLE[CMP-1:0]
    </span>
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d157801e118" rowspan="1">
    <span>
     <span class="documents-keyword">
      Address target group
     </span>
    </span>
    mapping
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 0
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="3">
    2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Traffic for groups 0,2 to MP 0
    </p>
    <p>
     Traffic for groups 1,3 to MP 1
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 0
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b01
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 1
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="4">
    3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Traffic for groups 0,3 to MP 0
    </p>
    <p>
     Traffic for groups 1,4 to MP 1
    </p>
    <p>
     Traffic for groups 2,5 to MP 2
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b110
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 0
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b101
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 1
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b011
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 2
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="7">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Traffic for groups 0,4 to MP 0
    </p>
    <p>
     Traffic for groups 1,5 to MP 1
    </p>
    <p>
     Traffic for groups 2,6 to MP 2
    </p>
    <p>
     Traffic for groups 3,7 to MP 3
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1100
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Traffic for groups 0, 2, 4, 6 to MP 0.
    </p>
    <p>
     Traffic for groups 1, 3, 5, 7 to MP 1.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0011
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Traffic for groups 0, 2, 4, 6 to MP 2.
    </p>
    <p>
     Traffic for groups 1, 3, 5, 7 to MP 3.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1110
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 0
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1101
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 1
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1011
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 2
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0111
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All traffic to MP 3
   </td>
  </tr>
 </tbody>
</table>
