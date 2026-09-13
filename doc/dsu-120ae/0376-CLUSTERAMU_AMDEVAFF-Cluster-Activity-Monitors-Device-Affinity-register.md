# CLUSTERAMU_AMDEVAFF, Cluster Activity Monitors Device Affinity register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVAFF--Cluster-Activity-Monitors-Device-Affinity-register>

### CLUSTERAMU\_AMDEVAFF, Cluster Activity Monitors Device Affinity register

Allows the external agent to determine which PE in a multiprocessor system the Activity Monitor component relates to.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   CLUSTERAMU

Register offset
:   0xFA8

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx x0xx xxx0 xxxx xxxx 1000 0000 0000 0000
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusteramu\_amdevaff bit assignments

![ext_clusteramu_amdevaff bit assignments](images/0376-CLUSTERAMU_AMDEVAFF-Cluster-Activity-Monitors-Device-Affinity-register-img01.svg)

<table id="vgw1733415019234__aclusteramu_amdevaff-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMDEVAFF bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d101774e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d101774e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d101774e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d101774e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:40]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgw1733415019234__63-40-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [39:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Aff3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Affinity level 3. Value read from the CFGMPIDRAFF3 configuration pins.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgw1733415019234__id-39-32-reset" rowspan="1">
    <code>
     8{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgw1733415019234__31-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    U
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uniprocessor/Multiprocessor system.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Processor is part of a multiprocessor system.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgw1733415019234__id-30-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [29:25]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgw1733415019234__29-25-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates whether the lowest level of affinity consists of logical PEs that are implemented using a multithreading type approach.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Activity of PEs at the lowest affinity level is largely independent.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgw1733415019234__id-24-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Aff2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Affinity level 2. Value read from the CFGMPIDRAFF2 configuration pins.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgw1733415019234__id-23-16-reset" rowspan="1">
    <code>
     8{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Aff1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Affinity level 1.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10000000
      </span>
     </dt>
     <dd>
      <p>
       Affinity with all cores in cluster.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="vgw1733415019234__id-15-8-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x80
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Aff0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Affinity level 0.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000
      </span>
     </dt>
     <dd>
      <p>
       Affinity with all core threads in cluster.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="vgw1733415019234__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
