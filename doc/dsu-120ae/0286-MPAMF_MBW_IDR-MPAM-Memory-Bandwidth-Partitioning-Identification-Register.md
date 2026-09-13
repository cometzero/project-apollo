# MPAMF_MBW_IDR, MPAM Memory Bandwidth Partitioning Identification Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-MBW-IDR--MPAM-Memory-Bandwidth-Partitioning-Identification-Register>

### MPAMF\_MBW\_IDR, MPAM Memory Bandwidth Partitioning Identification Register

Indicates which MPAM bandwidth partitioning features are present on this MSC. MPAMF\_MBW\_IDR\_s indicates bandwidth partitioning features accessed from the Secure MPAM feature page. MPAMF\_MBW\_IDR\_ns indicates bandwidth partitioning features accessed from the Non-secure MPAM feature page.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offsets (2)
:   0x0040,0x0040

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx x010 00xx xx00 0110
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_mpamf\_mbw\_idr bit assignments

![ext_mpamf_mbw_idr bit assignments](images/0286-MPAMF_MBW_IDR-MPAM-Memory-Bandwidth-Partitioning-Identification-Register-img01.svg)

<table id="sxf1733414935066__ampamf_mbw_idr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMF_MBW_IDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d119831e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:15]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sxf1733414935066__31-15-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [14]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    WINDWR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The bandwidth accounting period
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The bandwidth accounting period is not writeable.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sxf1733414935066__id-14-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [13]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    HAS_PROP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Proportional stride bandwidth partitioning
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Supports proportional stride bandwidth partitioning.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sxf1733414935066__id-13-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    HAS_PBM
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Bandwidth portion partitioning
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Does not support bandwidth portion partitioning.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sxf1733414935066__id-12-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    HAS_MAX
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Maximum bandwidth partitioning
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Does not support maximum bandwidth partitioning.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sxf1733414935066__id-11-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    HAS_MIN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Minimum bandwidth partitioning
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Does not support minimum bandwidth partitioning.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sxf1733414935066__id-10-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sxf1733414935066__9-6-reset" rowspan="1">
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
    CPBM_WD
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of implemented bits in the bandwidth allocation fields
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000110
      </span>
     </dt>
     <dd>
      <p>
       Supports 6 bits in the cache bandwidth allocation fields.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="sxf1733414935066__id-5-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000110
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
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e460" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e463" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e466" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d119831e469" rowspan="1">
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
    0x0040
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_MBW_IDR_s
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e517" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e520" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d119831e523" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d119831e526" rowspan="1">
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
    0x0040
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_MBW_IDR_ns
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
