# Attributes of the CHI peripheral port

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/Attributes-of-the-CHI-peripheral-port>

### Attributes of the CHI peripheral port

The read and write issuing capabilities of the CHI configured peripheral port depend on the configuration of the DynamIQ Shared Unit-120AE (DSU-120AE) at build time configuration, such as the number of L3 cache slices configured. For certain configurations, a maximum number of reads and writes can be up to 128 for the CHI configured peripheral port.

The following table lists the read and write transaction capabilities of the CHI configured peripheral port.

<table id="nyo1660577284926__table_chi_attributes">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Attributes of the CHI configured peripheral port
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d235288e74" rowspan="1">
    Attribute
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d235288e77" rowspan="1">
    Value
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d235288e80" rowspan="1">
    Comment
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Write issuing capability
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This can range up to a maximum of 128, depending on configuration.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Read issuing capability
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     This can range up to a maximum of 128, depending on configuration.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Exclusive hardware access thread capability
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Number of hardware threads
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Each hardware thread can have one exclusive access sequence in progress.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Transaction ID width
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    12 bits
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    There is no fixed mapping between CHI transaction IDs and
    <span>
     <span class="documents-keyword">
      cores
     </span>
    </span>
    . Transaction IDs can be used for either reads or writes.
    <blockquote title="Note info">
     <h3 class="documents-underline">
      Note
     </h3>
     The source of the transaction is encoded in the LPID field, see
     <a class="document-topic" document-topic-path="/107721/0001/CHI-requester-interface/CHI-transactions?lang=en#gvh1660577267936__table_lpid" href="/documentation/107721/0001/CHI-requester-interface/CHI-transactions?lang=en#gvh1660577267936__table_lpid">
      CHI LPID[4:0] bitfields
     </a>
     .
    </blockquote>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Transaction ID capability
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The transaction ID capability depends on the number of L3 cache slices configured, see the note following this table.
    </p>
    <p>
     There is never any ID reuse in CHI implementations, regardless of the memory type.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NodeID widths
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    11 bits
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TXREQFLIT.RSVDC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0 bits
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TXDATFLIT.RSVDC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0 bits
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    TXDATFLIT.DataCheck
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0 bits
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> - For the write issuing and read issuing capabilities, the total issuing capability of the cluster is the value of the `NUM_LTDBS` configuration parameter multiplied by the `NUM_L3_SLICES` parameter.
>
>   The peripheral port can support up to 128 transactions, or the total number of outstanding transaction for the cluster if this is less.
> - The issuing capability described in this table is the maximum for the whole cluster. If you want to achieve the maximum performance available, then you can use these values to size interconnect capabilities. However, this maximum issuing capability might not be reached by a single core on its own. It might need multiple cores generating heavy memory traffic simultaneously to reach the maximum value. The capabilities vary by core type, for example high-performance cores typically generate more transactions than balanced-performance cores. It can also vary by memory type, with typically a significantly lower limit for Device or Non-cacheable transactions than for Cacheable transactions.
