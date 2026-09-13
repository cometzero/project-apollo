# MPAMCFG_MBW_PROP_s, MPAM Memory Bandwidth Proportional Stride Partition Configuration for Secure PARTIDs

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-MBW-PROP-s--MPAM-Memory-Bandwidth-Proportional-Stride-Partition-Configuration-for-Secure-PARTIDs>

### MPAMCFG\_MBW\_PROP\_s, MPAM Memory Bandwidth Proportional Stride Partition Configuration for Secure PARTIDs

Controls the proportional stride of memory bandwidth that the PARTID selected by MPAMCFG\_PART\_SEL uses. MPAMCFG\_MBW\_PROP\_s controls the bandwidth proportional stride for the Secure PARTID selected by the Secure instance of MPAMCFG\_PART\_SEL. MPAMCFG\_MBW\_PROP\_ns controls the bandwidth proportional stride for the Non-secure PARTID selected by the Non-secure instance of MPAMCFG\_PART\_SEL.

Proportional stride is a relative cost of bandwidth requested by one PARTID in relation to the costs of the bandwidths requested by each other PARTID also competing to use the bandwidth.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offset
:   0x0500

Access type
:   RW

Reset value
:   ```
    0xxx xxxx xxxx xxxx xxxx xxxx xx00 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_mpamcfg\_mbw\_prop\_s bit assignments

![ext_mpamcfg_mbw_prop_s bit assignments](images/0291-MPAMCFG_MBW_PROP_s-MPAM-Memory-Bandwidth-Proportional-Stride-Partition-Configuration-for-Secure-PARTIDs-img01.svg)

<table id="sln1733414940144__ampamcfg_mbw_prop_s-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMCFG_MBW_PROP_s bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d18204e147" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18204e150" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18204e153" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d18204e156" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    EN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable proportional stride bandwidth partitioning.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The selected partition is not regulated by proportional stride bandwidth partitioning.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The selected partition has bandwidth usage regulated by proportional stride bandwidth partitioning as controlled by STRIDEM1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sln1733414940144__id-31-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sln1733414940144__30-6-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [5:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    STRIDEM1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Memory bandwidth stride minus 1 allocated to the partition selected by MPAMCFG_PART_SEL. STRIDEM1 represents the normalized cost of bandwidth consumption by the partition. The default value of 0 gives the maximum fair share of the bandwidth available to this partition. Larger values in this field indicate that this partition should receive a lower share of the overall bandwidth, relative to other partitions that have smaller values in this field.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="sln1733414940144__id-5-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d18204e285" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18204e288" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18204e291" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d18204e294" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0500
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMCFG_MBW_PROP_s
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
