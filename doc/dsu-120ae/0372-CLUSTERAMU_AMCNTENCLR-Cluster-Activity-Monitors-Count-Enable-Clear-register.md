# CLUSTERAMU_AMCNTENCLR, Cluster Activity Monitors Count Enable Clear register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMCNTENCLR--Cluster-Activity-Monitors-Count-Enable-Clear-register>

### CLUSTERAMU\_AMCNTENCLR, Cluster Activity Monitors Count Enable Clear register

Disables the implemented event counters CLUSTERAMEVCNTR<n>.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERAMU

Register offset
:   0xC20

Access type
:   RW

Reset value
:   ```
    0000 0000 0000 0000 0000 0000 000x xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusteramu\_amcntenclr bit assignments

![ext_clusteramu_amcntenclr bit assignments](images/0372-CLUSTERAMU_AMCNTENCLR-Cluster-Activity-Monitors-Count-Enable-Clear-register-img01.svg)

<table id="hmv1733415014632__aclusteramu_amcntenclr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMCNTENCLR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d65913e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d65913e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d65913e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d65913e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hmv1733415014632__31-5-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    A4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter disable bit for ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERAMU_AMCFGR.N is less than 32, bits [31:ext-CLUSTERAMU_AMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hmv1733415014632__id-4-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    A3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter disable bit for ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERAMU_AMCFGR.N is less than 32, bits [31:ext-CLUSTERAMU_AMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hmv1733415014632__id-3-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    A2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter disable bit for ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERAMU_AMCFGR.N is less than 32, bits [31:ext-CLUSTERAMU_AMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hmv1733415014632__id-2-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    A1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Event counter disable bit for ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERAMU_AMCFGR.N is less than 32, bits [31:ext-CLUSTERAMU_AMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hmv1733415014632__id-1-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    A0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Event counter disable bit for ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
    </p>
    <p>
     If ext-CLUSTERAMU_AMCFGR.N is less than 32, bits [31:ext-CLUSTERAMU_AMCFGR.N] are
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is disabled. When written, has no effect.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When read, means that ext-CLUSTERAMU_AMEVCNTR&lt;n&gt; is enabled. When written, disables ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="hmv1733415014632__id-0-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RW
