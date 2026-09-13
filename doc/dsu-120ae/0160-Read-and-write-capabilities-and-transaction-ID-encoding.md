# Read and write capabilities and transaction ID encoding

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/Read-and-write-capabilities-and-transaction-ID-encoding>

### Read and write capabilities and transaction ID encoding

The issuing capabilities and the AXI transaction ID encoding of the peripheral port depends on whether 64-bit mode or 256-bit mode is configured, and the number of cores configured in your cluster.

### 64-bit AXI peripheral port read and write capabilities

The maximum read or write issuing capability is 4 x (CN + 3), where CN is defined as follows:

- CN is the total number of cores in the cluster, including those in complexes, and can range from 1 to 14. Therefore, the maximum issuing capability for a cluster of 14 cores is 68 outstanding reads or writes.

The following table describes the read and write issuing capabilities of the peripheral port when configured as AXI 64-bit mode.

<table id="bgt1660577286473__table_fdk_gm5_zjb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   AXI issuing capabilities
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d178439e76" rowspan="1">
    Attribute
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d178439e79" rowspan="1">
    Value
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d178439e82" rowspan="1">
    Comments
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Write issuing capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4 x (CN + 3)
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="2">
    <blockquote id="bgt1660577286473__note_w929ab1b9b1c11b3b9b1b5b3_w930ab1b9b1c11b3b9b1b5_w931ab1b9b1c11b3b9b1_w932ab1b9b1c11b3b9_w933ab1b9b1c11b3_w934ab1b9b1c11_w935ab1b9b1_w936ab1b9_w937ab1" title="Note info">
     <h3 class="documents-underline">
      Note
     </h3>
     The DSU does not limit the amount of transactions from each source, provided that the total of all transactions does not exceed the maximum value for the configuration.
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Read issuing capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4 x (CN + 3)
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Write ID capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All transactions from a given LPID use the same AXI ID.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Read ID capability
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    All transactions from a given LPID use the same AXI ID.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    AWID width
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    6 bits
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    ARID width
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    6 bits
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
 </tbody>
</table>

The following table lists the encoding for AXI transaction IDs for the Peripheral port when configured as AXI 64-bit mode.

<table id="bgt1660577286473__table_ed4_zv5_zjb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   AXI transaction ID encoding
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d178439e186" rowspan="1">
    Attribute
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d178439e189" rowspan="1">
    Value
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d178439e192" rowspan="1">
    Comments
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    All IDs
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0xdd
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The encodings of dd are:
    </p>
    <dl id="bgt1660577286473__dl_fzt_5rx_12c">
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0x00
      </span>
      -
      <span class="documents-g.number.hex">
       0x0D
      </span>
     </dt>
     <dd>
      <span>
       Core
      </span>
      n, where n ranges 1 to 14.
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0x0E
      </span>
     </dt>
     <dd>
      L3 eviction
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0x0F
      </span>
     </dt>
     <dd>
      Accelerator Coherency Port (ACP) 0
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0x10
      </span>
     </dt>
     <dd>
      ACP 1
     </dd>
    </dl>
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> These ID and transaction details are provided for information only.
> Arm strongly recommends that all interconnects and peripherals are designed to support any type and number of transactions on any ID to ensure compatibility with future products.

### 256-bit AXI peripheral port read and write capabilities

See [AXI 256-bit manager interface attributes](/documentation/107721/0001/AXI-manager-interface/AXI-256-bit-manager-interface-attributes?lang=en "The read and write issuing capabilities of the AXI manager interface depend on the configuration of the DynamIQ Shared Unit-120AE (DSU-120AE) at build time configuration such as the number of L3 cache slices configured. For certain configurations, a maximum number of reads and writes can be up to approximately 128.") for the read and write issuing capabilities for a peripheral port configured in 256-bit mode.

See the  [AMBA® AXI Protocol Specification](https://developer.arm.com/documentation/ihi0022/latest/) for more information about the AXI signals described in this manual.
