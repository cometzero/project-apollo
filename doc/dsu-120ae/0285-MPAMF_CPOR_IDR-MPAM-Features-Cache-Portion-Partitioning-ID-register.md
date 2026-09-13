# MPAMF_CPOR_IDR, MPAM Features Cache Portion Partitioning ID register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-CPOR-IDR--MPAM-Features-Cache-Portion-Partitioning-ID-register>

### MPAMF\_CPOR\_IDR, MPAM Features Cache Portion Partitioning ID register

Indicates the number of bits in ext-MPAMCFG\_CPBM for this MSC. MPAMF\_CPOR\_IDR\_s indicates the number of bits in the Secure instance of ext-MPAMCFG\_CPBM. MPAMF\_CPOR\_IDR\_ns indicates the number of bits in the Non-secure instance of ext-MPAMCFG\_CPBM.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offsets (2)
:   0x0030,0x0030

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx 0000 0000 0000 1000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_mpamf\_cpor\_idr bit assignments

![ext_mpamf_cpor_idr bit assignments](images/0285-MPAMF_CPOR_IDR-MPAM-Features-Cache-Portion-Partitioning-ID-register-img01.svg)

<table id="sqz1733414933594__ampamf_cpor_idr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMF_CPOR_IDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d10413e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="sqz1733414933594__31-16-reset" rowspan="1">
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
    CPBM_WD
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of bits in the cache portion partitioning bit map of this device. See ext-MPAMCFG_CPBM.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000000000001000
      </span>
     </dt>
     <dd>
      <p>
       Supports 8 cache portion partitioning bits.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="sqz1733414933594__id-15-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x0008
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
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e243" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e246" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e249" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d10413e252" rowspan="1">
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
    0x0030
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_CPOR_IDR_s
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
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e300" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e303" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10413e306" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d10413e309" rowspan="1">
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
    0x0030
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_CPOR_IDR_ns
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
