# MPAMCFG_PART_SEL, MPAM Partition Configuration Selection Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-PART-SEL--MPAM-Partition-Configuration-Selection-Register>

### MPAMCFG\_PART\_SEL, MPAM Partition Configuration Selection Register

Selects a partition ID to configure. MPAMCFG\_PART\_SEL\_s selects a Secure PARTID to configure. MPAMCFG\_PART\_SEL\_ns selects a Non-secure PARTID to configure.

After setting this register with a PARTID, software (usually a hypervisor) can perform a series of accesses to MPAMCFG registers to configure parameters for MPAM resource controls to use when requests have that PARTID.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offsets (2)
:   0x0100,0x0100

Access type
:   See bit descriptions

Reset value
:   ```
    xxxx xxxx xxxx xxx0 xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_mpamcfg\_part\_sel bit assignments

![ext_mpamcfg_part_sel bit assignments](images/0289-MPAMCFG_PART_SEL-MPAM-Partition-Configuration-Selection-Register-img01.svg)

<table id="lyy1733414937948__ampamcfg_part_sel-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMCFG_PART_SEL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e147" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e150" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e153" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d219188e156" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:17]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lyy1733414937948__31-17-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INTERNAL
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Internal PARTID. This field is
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
       PARTID_SEL is interpreted as a request PARTID and ignored except for use with ext-MPAMCFG_INTPARTID register access.
      </p>
     </dd>
    </dl>
    <p>
     Access to this field is:
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lyy1733414937948__id-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [15:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PARTID_SEL
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Selects the partition ID to configure.
    </p>
    <p>
     Reads and writes to other MPAMCFG registers are indexed by PARTID_SEL and by the NS bit used to access MPAMCFG_PART_SEL to access the configuration for a single partition.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="lyy1733414937948__id-15-0-reset" rowspan="1">
    <code>
     16{x}
    </code>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e279" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e282" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e285" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d219188e288" rowspan="1">
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
    0x0100
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMCFG_PART_SEL_s
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e336" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e339" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d219188e342" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d219188e345" rowspan="1">
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
    0x0100
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMCFG_PART_SEL_ns
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
