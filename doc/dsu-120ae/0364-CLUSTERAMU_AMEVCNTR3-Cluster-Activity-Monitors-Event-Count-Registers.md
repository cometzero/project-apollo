# CLUSTERAMU_AMEVCNTR3, Cluster Activity Monitors Event Count Registers

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMEVCNTR3--Cluster-Activity-Monitors-Event-Count-Registers>

### CLUSTERAMU\_AMEVCNTR3, Cluster Activity Monitors Event Count Registers

Holds event counter 3, which counts events.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   CLUSTERAMU

Register offset
:   0x18

Access type
:   RW

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusteramu\_amevcntr3 bit assignments

![ext_clusteramu_amevcntr3 bit assignments](images/0364-CLUSTERAMU_AMEVCNTR3-Cluster-Activity-Monitors-Event-Count-Registers-img01.svg)

<table id="wqn1733415006419__aclusteramu_amevcntr3-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMEVCNTR3 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d84732e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84732e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d84732e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d84732e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [63:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    AMEVCNTR
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Event counter 3.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="wqn1733415006419__id-63-0-reset-1" rowspan="1">
    <code>
     64{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RW
