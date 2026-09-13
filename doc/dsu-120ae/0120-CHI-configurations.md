# CHI configurations

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/CHI-configurations>

### CHI configurations

You can change the coherency configurations to suit your system configuration using the BROADCASTCACHEMAINT and BROADCASTOUTER input signals.

The following table shows the permitted combinations of these signals and the supported configurations in the DynamIQ Shared Unit-120AE (DSU-120AE), with a CHI bus.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Supported CHI configurations
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d73836e85" rowspan="3">
    Signal
   </th>
   <th class="documents-cell-norowborder" colspan="4" id="d73836e88" rowspan="1">
    Feature
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="2" id="d73836e94" rowspan="1">
    CHI non-coherent
   </th>
   <th class="documents-cell-norowborder" colspan="2" id="d73836e97" rowspan="1">
    CHI coherent
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d73836e103" rowspan="1">
    <p>
     With no cache or invisible system cache
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d73836e109" rowspan="1">
    <p>
     With visible system cache
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d73836e115" rowspan="1">
    <p>
     With invisible system cache
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d73836e121" rowspan="1">
    <p>
     With visible system cache
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTCACHEMAINT
     </span>
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    1
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTOUTER
     </span>
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> - A visible system cache requires cache maintenance transactions to ensure that a write is visible to all observers.
> - An invisible system cache is one that does not require cache maintenance transactions to ensure that a write is visible to all observers. This is true even if those observers use different memory attributes.

The following table shows the key features in each of the supported CHI configurations.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Supported features in the CHI configurations
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
   <th class="documents-nocellnorowborder" colspan="1" id="d73836e206" rowspan="3">
    Features
   </th>
   <th class="documents-cell-norowborder" colspan="3" id="d73836e209" rowspan="1">
    Configuration
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="2" id="d73836e215" rowspan="1">
    CHI non-coherent
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d73836e218" rowspan="2">
    CHI coherent
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d73836e224" rowspan="1">
    With no cache or invisible system cache
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d73836e227" rowspan="1">
    With visible system cache
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Cache maintenance requests on TXREQ channel
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Yes
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Snoops on RXSNP channel
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Coherent requests on TXREQ channel
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    No
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Yes
   </td>
  </tr>
 </tbody>
</table>

The input signals BROADCASTTLBIINNER and BROADCASTTLBIOUTER control the broadcasting of TLB Invalidate (TLBI) DVM messages to the external interconnect. The following table shows how the broadcast of the TLBI messages is controlled for the Inner and Outer Shareable domains depending on the configuration of BROADCASTTLBIINNER and BROADCASTTLBIOUTER.

<table id="ibo1660577266659__table_a4v_qcy_hjb">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   Control of Inner and Outer Shareable TLBI messages to the external interconnect
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d73836e319" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTTLBIINNER
     </span>
    </span>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d73836e323" rowspan="1">
    <span class="documents-g.signal.name">
     <span class="documents-keyword">
      BROADCASTTLBIOUTER
     </span>
    </span>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d73836e327" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    LOW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    LOW
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    No TLBI transactions are broadcast outside the cluster.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    LOW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    HIGH
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Outer Shareable TLBI transactions, TLBI {OS}, generate TLBI transactions that are broadcast from the cluster. No other TLBI instructions generate TLB transactions that are broadcast from the cluster.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    HIGH
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    LOW
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Invalid configuration
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    HIGH
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    HIGH
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Inner Shareable TLBI instructions, TLBI {IS}, and Outer Shareable TLBI instructions, TLBI {OS}, generate TLBI transactions that are broadcast from the cluster.
   </td>
  </tr>
 </tbody>
</table>
