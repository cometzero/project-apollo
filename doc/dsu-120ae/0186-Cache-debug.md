# Cache debug

Source: <https://developer.arm.com/documentation/107721/0001/Debug/Cache-debug>

### Cache debug

Cache debug of the DSU-120AE cache RAMs is supported, which allows software to read the contents of the L3 cache and snoop filter (SF) RAMs. This cache debug is under control of the core, in the same way that the L1 or L2 cache debug is controlled. Access to the DSU-120AE cache debug information is provided through the DSU-120AE CLUSTERCDBG register.

The three-step process of extracting information from the RAMs is as follows:

1. The core writes to the CLUSTERCDBG register, setting the bit fields for the physical location it wants to retrieve the data from. See the following table for bit field values.
2. The DSU-120AE returns the RAM contents in the CLUSTERCDBG register in an encoded form.
3. The core reads this information from the CLUSTERCDBG register.

> ### Note
>
> - The bit field descriptions for the CLUSTERCDBG register depend on if you are writing to the register or reading from the register, and when you are reading from the register what type of access is being made.
> - The CLUSTERCDBG register is shared between cores, so to get predictable results software must ensure that only one core accesses the register at a time.
> - The cache debug operations only reads the cache contents when the cluster is in the ON power mode. If the cluster is in FUNC\_RET power mode or FULL\_RET power mode, the contents of the CLUSTERCDBG register are UNKNOWN. Therefore, Arm recommends before starting any cache debug accesses that software sets the IMP\_CLUSTERPWRCTLR\_EL1.FUNCRET and IMP\_CLUSTERPWRCTLR\_EL1.FULLRET values to zero.

The following table describes the bit fields for the CLUSTERCDBG register when writing to the register:

<table id="fni1660577302055__table_htj_g4l_f4b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERCDBG bit descriptions when writing to the register
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d19060e132" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d19060e135" rowspan="1">
    Name
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d19060e138" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RAZ/WI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WAY
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Way of RAM being accessed.
    </p>
    <p>
     The number of SF ways can be obtained from the IMP_CLUSTERCFR_EL1 register. The number of L3 cache ways can be obtained from the CCSIDR_EL1 register.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RAZ/WI
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Reserved
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SLCID_IDX
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The L3 cache Set locations in each cache slice are all power-of-2 in size and therefore can be identified using contiguous index locations. The Set index values for slice 0 start from value zero in this field, followed by the index locations for slice 1, and then sequentially up to the total number of cache slices.
    </p>
    <p>
     The total index width varies depending on the size of the RAM being accessed. The cache slice identification number, slice ID, forms the upper used bits of the cache location encoding in this field. For details on tag index widths, see
     <a class="document-topic" document-topic-path="/107721/0001/Debug/Cache-debug?lang=en#fni1660577302055__table_tagindex" href="/documentation/107721/0001/Debug/Cache-debug?lang=en#fni1660577302055__table_tagindex">
      Tag index width for L3 RAM accesses
     </a>
     . For details on slice ID widths see
     <a class="document-topic" document-topic-path="/107721/0001/Debug/Cache-debug?lang=en#fni1660577302055__table_sliceid" href="/documentation/107721/0001/Debug/Cache-debug?lang=en#fni1660577302055__table_sliceid">
      Slice ID width
     </a>
     .
    </p>
    <p>
     As the SF RAM sizes are, typically, different from the L3 RAM sizes, the precise encodings of this field will be different when accessing SF RAM locations compared with accessing L3 cache tag and data RAM locations. For details on the SF index widths, see
     <a class="document-topic" document-topic-path="/107721/0001/Debug/Cache-debug?lang=en#fni1660577302055__table_sfindex" href="/documentation/107721/0001/Debug/Cache-debug?lang=en#fni1660577302055__table_sfindex">
      SF index width for SF RAM accesses
     </a>
     .
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5:3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CHUNK
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Select of 64-bit data chunk to read from 512-bit Data RAM cache line. Only used when accessing Data RAM data.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       Data[63:0]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       Data[127:64]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       Data[191:128]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       Data[255:192]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b100
      </span>
     </dt>
     <dd>
      <p>
       Data[319:256]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101
      </span>
     </dt>
     <dd>
      <p>
       Data[383:320]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b110
      </span>
     </dt>
     <dd>
      <p>
       Data[447:384]
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       Data[511:448]
      </p>
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [2:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RAM
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     RAM to be accessed. All other values are reserved.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       Snoop Filter RAM
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       Tag RAM
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       Data RAM - accessing cacheline data
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       Data RAM - accessing cacheline Memory Tagging Extension (MTE) tags
      </p>
     </dd>
    </dl>
   </td>
  </tr>
 </tbody>
</table>

The following table shows how to determine the slice ID width from the number of cache slices configured:

<table id="fni1660577302055__table_sliceid">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Slice ID width
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d19060e463" rowspan="1">
    Number of cache slices
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e466" rowspan="1">
    Slice ID width
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    0
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    8
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    3
   </td>
  </tr>
 </tbody>
</table>

For L3 RAM accesses, the following table shows how to determine the tag index width from the cache size per slice:

> ### Note
>
> In the following table, the L3 Tag RAM address width for the 3072KB and 4096KB sizes is only 11-bits wide, but there are two banks of RAMs, so the effective width is 12-bits. For these configurations, the Least Significant Bit (LSB) of the SLCID\_IDX field selects which bank to access.

<table id="fni1660577302055__table_tagindex">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   Tag index width for L3 RAM accesses
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d19060e536" rowspan="1">
    Cache size per slice
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e539" rowspan="1">
    Tag index width
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    256KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    8
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    384KB-512KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    9
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    768KB-1024KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    10
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1536KB-2048KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    11
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    3072KB-4096KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    12
   </td>
  </tr>
 </tbody>
</table>

For SF RAM accesses, the following table shows how to determine the snoop filter index widths from the cache size per slice:

> ### Note
>
> In the following table, the snoop filter RAM address width for the 1536KB and 2048KB sizes is only 11-bits wide, but there are two banks of RAMs, so the effective width is 12-bits. The snoop filter RAM address width is also 11-bits for the 3072kB and 4096kB sizes, but there are four banks, so the effective width is 13-bits. For these configurations, the Least Significant Bit (LSB) of the SLCID\_IDX field selects which bank to access.

<table id="fni1660577302055__table_sfindex">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 4.
   </span>
   SF index width for SF RAM accesses
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d19060e619" rowspan="1">
    SF size per slice
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e622" rowspan="1">
    SF index width
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    128KB, 192KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    9
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    256KB, 384KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    10
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    512KB, 768KB, 1024KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    11
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1536KB, 2048KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    12
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    3072KB, 4096KB
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    13
   </td>
  </tr>
 </tbody>
</table>

The following table describes how to interpret RAM data read back from the DSU-120AE CLUSTERCDBG register, for a snoop filter access:

<table id="fni1660577302055__table_trn_2sl_f4b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 5.
   </span>
   CLUSTERCDBG bit descriptions for a snoop filter RAM access
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d19060e700" rowspan="1">
    Bits
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e703" rowspan="1">
    Width (bits)
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e706" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [63:MAX_CMPXS+40]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    24 - MAX_CMPXS
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    RAZ
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [MAX_CMPXS+39:40]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MAX_CMPXS
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    One bit per standalone
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    or per
    <span>
     <span class="documents-keyword">
      complex
     </span>
    </span>
    . When a bit is 1 it identifies a
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    or
    <span>
     <span class="documents-keyword">
      complex
     </span>
    </span>
    where the cache line is allocated. When a bit is 0 it indicates the cache line is not allocated in this
    <span>
     <span class="documents-keyword">
      core
     </span>
    </span>
    or
    <span>
     <span class="documents-keyword">
      complex
     </span>
    </span>
    .
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [39:38]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     This field has the following values:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      Cache line is invalid
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      Cluster received a shared copy of the cache line. The
      <span>
       <span class="documents-keyword">
        cores
       </span>
      </span>
      know it is shared.
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      Cluster received a unique copy of the cache line and has given a unique copy to a
      <span>
       <span class="documents-keyword">
        core
       </span>
      </span>
      or
      <span>
       <span class="documents-keyword">
        complex
       </span>
      </span>
      (the
      <span>
       <span class="documents-keyword">
        core
       </span>
      </span>
      thinks it is unique).
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      Cluster received a unique copy of the cache line and has given a shared copy to one or more
      <span>
       <span class="documents-keyword">
        complexes
       </span>
      </span>
      (the
      <span>
       <span class="documents-keyword">
        core
       </span>
      </span>
      thinks it is shared).
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [37:26]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    12
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    RAZ
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [25]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     NS (Non-Secure). This bit has the following values:
    </p>
    <dl>
     <dt class="documents-dlterm">
      0
     </dt>
     <dd>
      The cache line is Secure
     </dd>
     <dt class="documents-dlterm">
      1
     </dt>
     <dd>
      The cache line is Non-secure
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [24:0]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    25
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Physical address tag. The encoding of these bits depends on IMP_CLUSTERCFR_EL1.SFIDX as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0x9
      </span>
     </dt>
     <dd>
      <code>
       {PA[39:15}
      </code>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0xA
      </span>
     </dt>
     <dd>
      <code>
       {PA[39:16},1'b0}
      </code>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0xB
      </span>
     </dt>
     <dd>
      <code>
       {PA[39:17},2'b00}
      </code>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.hex">
       0xC
      </span>
     </dt>
     <dd>
      <code>
       {PA[39:18},3'b000}
      </code>
     </dd>
    </dl>
   </td>
  </tr>
 </tbody>
</table>

The following table describes how to interpret RAM data read back from the DSU-120AE CLUSTERCDBG register, for a tag RAM access:

<table id="fni1660577302055__table_bp2_3mm_f4b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 6.
   </span>
   CLUSTERCDBG bit descriptions for a tag RAM access
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d19060e981" rowspan="1">
    Bits
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e984" rowspan="1">
    Width (bits)
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e987" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [63:58]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    6
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    RAZ
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [57]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Memory System Resource Partitioning and Monitoring (MPAM) - PMG bit. If MPAM values are stored in the cache, then this bit saves the MPAM PMG value.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [56:51]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    6
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MPAM - PartID. If MPAM values are stored in the cache, then these bits save the MPAM PARTID value.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [50]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MPAM - NS. If MPAM values are stored in the L3 cache, this bit indicates if it is a Non-secure state PARTID or a Secure state PARTID.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [49:46]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Page-Based Hardware Attribute (PBHA). If the PBHA bits are stored in the cache, then these bits report the PBHA values for this cache line.
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [45:44]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     MTE state. If MTE values are stored in the cache, then these bits save the MTE values for this line. The possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      MTE tag is Invalid
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      MTE tag is Clean
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      MTE tag is Dirty (the tag value for the cache line has been modified using an instruction such as
      <code>
       STG
      </code>
      .
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [43]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     OA (Outer Allocation). The possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      0
     </dt>
     <dd>
      This hints that the system should not allocate the cache line.
     </dd>
     <dt class="documents-dlterm">
      1
     </dt>
     <dd>
      This hints that the system should allocate the cache line.
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [42]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     PF (PreFetch). The possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      0
     </dt>
     <dd>
      This hints that the cache line is not considered to be a prefetch (the cache line has been used).
     </dd>
     <dt class="documents-dlterm">
      1
     </dt>
     <dd>
      This hints that the cache line is an unused prefetch.
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [41]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     CP (CPU Presence). The possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      0
     </dt>
     <dd>
      Indicates that there is no snoop filter entry for this cache line.
     </dd>
     <dt class="documents-dlterm">
      1
     </dt>
     <dd>
      Indicates a snoop filter entry for this cache line.
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [40:39]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Tag RAM State. The possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      Cache line entry Invalid
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      UniqueDirty. The cluster has a unique, modified (dirty) copy of the cache line.
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      SharedClean. The cluster has a shared copy of the cache line that is coherent with the external memory location.
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      UniqueClean. The cluster has a unique copy of the cache line.
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [38:27]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    12
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    RAZ
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [26]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    12
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     NS (Non-Secure). The possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      0
     </dt>
     <dd>
      The cache line is Secure.
     </dd>
     <dt class="documents-dlterm">
      0
     </dt>
     <dd>
      The cache line is Non-secure.
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [25:0]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    26
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Physical Address Tag
    </p>
    <p>
     Encoding varies depending on the number of L3 sets divided by the number of L3 cache slices. The number of L3 sets can be found by writing
     <span class="documents-g.number.hex">
      0x4
     </span>
     to CSSELR_EL1, and then calculating CCSIDR_EL1.NumSets + 1. The number of L3 cache slices can be found from the IMP_CLUSTERCFR_EL1.L3SLC.
    </p>
    <p>
     For (L3 sets/L3 cache slices), the possible values are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      256
     </dt>
     <dd>
      {PA[39:14]}
     </dd>
     <dt class="documents-dlterm">
      512
     </dt>
     <dd>
      {PA[39:15],1'b0}
     </dd>
     <dt class="documents-dlterm">
      1024
     </dt>
     <dd>
      {PA[39:16],2'b00}
     </dd>
     <dt class="documents-dlterm">
      2048
     </dt>
     <dd>
      {PA[39:17],3'b000}
     </dd>
    </dl>
    <p>
     Where PA is the Physical Address width.
    </p>
   </td>
  </tr>
 </tbody>
</table>

The following table describes how to interpret the data read back from the DSU-120AE CLUSTERCDBG register, for a Data RAM data access:

<table id="fni1660577302055__table_mmp_tft_h4b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 7.
   </span>
   CLUSTERCDBG bit descriptions for a Data RAM data access
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d19060e1418" rowspan="1">
    Bits
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e1421" rowspan="1">
    Width (bits)
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e1424" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [63:0]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    64
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    Cache data from selected cache location and Chunk of data
   </td>
  </tr>
 </tbody>
</table>

The following table describes how to interpret the data read back from the DSU-120AE CLUSTERCDBG register, for a Data RAM tag value access:

<table id="fni1660577302055__table_wqw_hjt_h4b">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 8.
   </span>
   CLUSTERCDBG bit descriptions for a Data RAM MTE tag value access
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cellrowborder" colspan="1" id="d19060e1469" rowspan="1">
    Bits
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e1472" rowspan="1">
    Width (bits)
   </th>
   <th class="documents-cellrowborder" colspan="1" id="d19060e1475" rowspan="1">
    Description
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [63:16]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    -
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    RAZ
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [15:12]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MTE tag for selected cache line bits [511:384]
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [11:8]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MTE tag for selected cache line bits [383:256]
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MTE tag for selected cache line bits [255:128]
   </td>
  </tr>
  <tr>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    4
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    MTE tag for selected cache line bits [127:0]
   </td>
  </tr>
 </tbody>
</table>
