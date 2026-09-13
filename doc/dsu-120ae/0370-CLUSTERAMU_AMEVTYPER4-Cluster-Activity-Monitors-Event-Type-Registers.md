# CLUSTERAMU_AMEVTYPER4, Cluster Activity Monitors Event Type Registers

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVTYPER4--Cluster-Activity-Monitors-Event-Type-Registers>

### CLUSTERAMU\_AMEVTYPER4, Cluster Activity Monitors Event Type Registers

Configures event counter n, where n is 0 to 31.

### Configurations

If event counter n is not implemented then accesses to this register are RES0.

### Attributes

Width
:   32

Component
:   CLUSTERAMU

Register offset
:   0x410

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusteramu\_amevtyper4 bit assignments

![ext_clusteramu_amevtyper4 bit assignments](images/0370-CLUSTERAMU_AMEVTYPER4-Cluster-Activity-Monitors-Event-Type-Registers-img01.svg)

<table id="zdc1733415012792__aclusteramu_amevtyper4-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMEVTYPER4 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d6878e144" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d6878e147" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d6878e150" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d6878e153" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zdc1733415012792__31-16-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [15:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    evtCount
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Event to count. The event number of the event that is counted by event counter ext-CLUSTERAMU_AMEVCNTR&lt;n&gt;.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="zdc1733415012792__id-15-0-reset" rowspan="1">
    <code>
     16{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
