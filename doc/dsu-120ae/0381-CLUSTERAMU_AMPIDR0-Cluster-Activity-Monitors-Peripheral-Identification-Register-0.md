# CLUSTERAMU_AMPIDR0, Cluster Activity Monitors Peripheral Identification Register 0

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR0--Cluster-Activity-Monitors-Peripheral-Identification-Register-0>

### CLUSTERAMU\_AMPIDR0, Cluster Activity Monitors Peripheral Identification Register 0

Provides information to identify a Activity Monitor component.

### Configurations

This register is required for CoreSight compliance.

### Attributes

Width
:   32

Component
:   CLUSTERAMU

Register offset
:   0xFE0

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 1110 1100
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusteramu\_ampidr0 bit assignments

![ext_clusteramu_ampidr0 bit assignments](images/0381-CLUSTERAMU_AMPIDR0-Cluster-Activity-Monitors-Peripheral-Identification-Register-0-img01.svg)

<table id="itf1733415023828__aclusteramu_ampidr0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMPIDR0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d81407e144" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d81407e147" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d81407e150" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d81407e153" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="itf1733415023828__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PART_0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Part number bits [7:0].
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11101100
      </span>
     </dt>
     <dd>
      <p>
       DSU-120AE Cluster AMU. Bits [7:0] of part number 0x4EC.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="itf1733415023828__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0xEC
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
