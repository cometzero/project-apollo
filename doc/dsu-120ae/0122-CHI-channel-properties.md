# CHI channel properties

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/CHI-channel-properties>

### CHI channel properties

The CHI requester interface supports snoops from your external memory system. The DynamIQ Shared Unit-120AE (DSU-120AE) supports all snoop request types listed in the CHI Issue E protocol.

The following table describes the snoop capabilities and other CHI properties of the DSU-120AE.

<table id="kbz1660577267508__table_usr_cml_xz">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CHI channel properties
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d11550e80" rowspan="1">
    Property
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d11550e83" rowspan="1">
    Value
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d11550e86" rowspan="1">
    Comment
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Snoop acceptance capability
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Configuration dependent
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The total snoop acceptance capability of the cluster is the value of the
     <code>
      NUM_LTDBS
     </code>
     configuration parameter multiplied by the
     <code>
      NUM_L3_SLICES
     </code>
     parameter.
    </p>
    <p>
     Each
     <span class="documents-keyword">
      requester
     </span>
     port can accept up to this overall limit, however it has more limited tracking of the SrcID field of the snoops. Therefore, if there are snoops outstanding from 15 different other components in the system, then any snoop from a 16th or further component will not be accepted. The number of snoops from each component is only limited by the total cluster acceptance capability.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DVM acceptance capability
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Four per
    <span class="documents-keyword">
     requester
    </span>
    port
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The SCU can accept and process a maximum of four DVM transactions per
     <span class="documents-keyword">
      requester
     </span>
     port from the system. Each of these four transactions can be a two part DVM message.
    </p>
    <p>
     The interconnect must be configured to never send more than four DVM messages to a CHI
     <span class="documents-keyword">
      requester
     </span>
     interface port, otherwise the system might deadlock.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="3">
    Snoop latency
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Hit and miss latencies depend on configuration
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Snoop latencies depend on how many
     <span class="documents-keyword">
      requester
     </span>
     interfaces are configured, and if the snoops miss in the cluster, hit in the L3 cache, or hit in L1 or L2 caches of the
     <span>
      <span class="documents-keyword">
       cores
      </span>
     </span>
     .
    </p>
    <p>
     Snoops that hit in the L1 or L2 caches of a
     <span>
      <span class="documents-keyword">
       core
      </span>
     </span>
     have a higher latency. This latency depends on the type of core, and whether the hit is in the L1 or L2 cache. Typically the rate sustained is at least half that for the L3 cache bandwidth.
    </p>
    <p>
     Latencies can be higher if hazards occur or if there are not enough buffers to absorb requests.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Miss
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Dependent on build-time configuration
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DVM
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Dependent on build-time configuration
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Snoop filter
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Supported
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The cluster supports an external snoop filter in an interconnect. It indicates when clean lines are evicted from the cluster by sending Evict transactions on the CHI write channel.
    </p>
    <p>
     However there are some cases that can prevent an Evict transaction from being sent. Therefore you must ensure that you build any external snoop filter to handle a capacity overflow. When exceeding capacity, the snoop filter should send a back-invalidation to the cluster.
    </p>
    <p>
     Examples of case where evicts are not produced include:
    </p>
    <ul id="kbz1660577267508__ul_vsr_cml_xz">
     <li>
      Linefills that take External aborts.
     </li>
     <li>
      Store exclusives that fail.
     </li>
     <li>
      Mis-matched aliases.
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Supported transactions
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The
     <span class="documents-keyword">
      DSU-120AE
     </span>
     supports all transaction types produced by the CHI protocol.
    </p>
   </td>
  </tr>
 </tbody>
</table>
