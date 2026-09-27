# CryptoCell Lifecycle Indication interface

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces/CryptoCell-Related-Expansion-interfaces/CryptoCell-Lifecycle-Indication-interface>

### CryptoCell Lifecycle Indication interface

The CryptoCell Lifecycle Indication interface indicates the lifecycle state of the system through different stages of manufacture and deployment of the final product.

All signals are synchronous to CRYPTOSYSCLK and are on the Always ON power domain.

The following table shows the output signals on the CryptoCell Lifecycle Indication interface.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CryptoCell Lifecycle Indication interface
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d130787e70" rowspan="1">
    <p>
     Signal name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d130787e74" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d130787e78" rowspan="1">
    <p>
     Direction
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d130787e82" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CRYPTOLCS[2:0]
      </span>
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Lifecycle State values:
    </p>
    <ul>
     <li>
      <p>
       3&rsquo;b000 Chip Manufacture (CM)
      </p>
     </li>
     <li>
      <p>
       3&rsquo;b001 Device Manufacture (DM)
      </p>
     </li>
     <li>
      <p>
       3&rsquo;b101 Secure Enable (SE)
      </p>
     </li>
     <li>
      <p>
       3&rsquo;b111 Return to Manufacturer (RMA)
      </p>
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CRYPTOLCSVALID
      </span>
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Output
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Lifecycle State values on
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       CRYPTOLCS
      </span>
     </span>
     is valid, where:
    </p>
    <ul>
     <li>
      <p>
       &lsquo;1&rsquo;
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         CRYPTOLCS[2:0]
        </span>
       </span>
       is valid.
      </p>
     </li>
     <li>
      <p>
       &lsquo;0&rsquo;
       <span class="documents-g.signal.name">
        <span class="documents-keyword">
         CRYPTOLCS[2:0]
        </span>
       </span>
       is not valid.
      </p>
     </li>
    </ul>
   </td>
  </tr>
 </tbody>
</table>
