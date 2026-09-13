# AXI 256-bit manager interface attributes

Source: <https://developer.arm.com/documentation/107721/0001/AXI-manager-interface/AXI-256-bit-manager-interface-attributes>

### AXI 256-bit manager interface attributes

The read and write issuing capabilities of the AXI manager interface depend on the configuration of the DynamIQ Shared Unit-120AE (DSU-120AE) at build time configuration such as the number of L3 cache slices configured. For certain configurations, a maximum number of reads and writes can be up to approximately 128.

The following table shows the AXI manager interface attributes.

<table id="dmm1660577273938__table_w2057ab1b9b1b3_w2058ab1b9b1_w2059ab1b9_w2060ab1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   AXI 256-bit
   <span class="documents-keyword">
    manager
   </span>
   interface attributes
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-row-nocellborder" colspan="1" id="d270843e86" rowspan="1">
    Attribute
   </th>
   <th class="documents-row-nocellborder" colspan="1" id="d270843e89" rowspan="1">
    Value
   </th>
   <th class="documents-row-nocellborder" colspan="1" id="d270843e92" rowspan="1">
    Comments
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Write issuing capability
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     This value can range up to a maximum of 128, depending on configuration. A maximum of 56 non-reorderable Device write transactions can be issued.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Read issuing capability
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     This value can range up to a maximum of 128, depending on configuration. A maximum of 68 outstanding non-reorderable Device read transactions can be issued.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Write ID capability
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Only Device memory types with nGnRnE or nGnRE can have more than one outstanding transaction with the same AXI ID. All other memory types use a unique AXI ID for every outstanding transaction.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Read ID capability
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Only Device memory types with nGnRnE or nGnRE can have more than one outstanding transaction with the same AXI ID. All other memory types use a unique AXI ID for every outstanding transaction.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AWID width
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    10 bits
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ARID width
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    10 bits
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> For the read issuing and write issuing capabilities, the total issuing capability of the cluster is the value of the `NUM_LTDBS` configuration parameter multiplied by the `NUM_L3_SLICES` parameter. If there is only one manager port configured, then it can support the total number of outstanding transactions. For multiple-manager configurations the percentage of total outstanding transactions each manager can support is as follows:
>
> - If there is only one manager port configured, then it can support the total number of outstanding transactions.
> - If there are two manager ports configured, then each port can support up to 50% of the total outstanding transactions.
> - If there are three manager ports configured, then each port can support up to 33% of the total outstanding transactions.
> - If there are four manager ports configured, then each port can support up to 25% of the total outstanding transactions.
>
> The peripheral port can support up to 128 transactions, or the total number of cluster outstanding transaction if this is less.

For more information about the AXI signals described in this manual, see the  [AMBA® AXI Protocol Specification](https://developer.arm.com/documentation/ihi0022/latest/).
