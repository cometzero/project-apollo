# CLUSTERAMU_AMPIDR4, Cluster Activity Monitors Peripheral Identification Register 4

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR4--Cluster-Activity-Monitors-Peripheral-Identification-Register-4>

### CLUSTERAMU\_AMPIDR4, Cluster Activity Monitors Peripheral Identification Register 4

Provides information to identify a Activity Monitor component.

### Configurations

This register is required for CoreSight compliance.

### Attributes

Width
:   32

Component
:   CLUSTERAMU

Register offset
:   0xFD0

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 0100
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusteramu\_ampidr4 bit assignments

![ext_clusteramu_ampidr4 bit assignments](images/0380-CLUSTERAMU_AMPIDR4-Cluster-Activity-Monitors-Peripheral-Identification-Register-4-img01.svg)

<table id="tgp1733415022916__aclusteramu_ampidr4-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMPIDR4 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d292168e144" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d292168e147" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d292168e150" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d292168e153" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="tgp1733415022916__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SIZE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4KB count.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       The component uses a single 4KB block.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="tgp1733415022916__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    DES_2
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     JEP106 continuation code.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       Arm Limited. Number of 0x7F bytes in full JEP106 code 0x7F 0x7F 0x7F 0x7F 0x3B.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="tgp1733415022916__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0100
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
