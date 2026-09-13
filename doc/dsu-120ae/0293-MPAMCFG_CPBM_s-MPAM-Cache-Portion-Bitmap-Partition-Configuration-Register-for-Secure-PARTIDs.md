# MPAMCFG_CPBM_s, MPAM Cache Portion Bitmap Partition Configuration Register for Secure PARTIDs

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-CPBM-s--MPAM-Cache-Portion-Bitmap-Partition-Configuration-Register-for-Secure-PARTIDs>

### MPAMCFG\_CPBM\_s, MPAM Cache Portion Bitmap Partition Configuration Register for Secure PARTIDs

The MPAMCFG\_CPBM register is a read-write register that configures the cache portions that a PARTID is allowed to allocate. After setting ext-MPAMCFG\_PART\_SEL with a PARTID, software (usually a hypervisor) writes to the MPAMCFG\_CPBM register to configure which cache portions the PARTID is allowed to allocate.

MPAMCFG\_CPBM\_s controls cache portions for the Secure PARTID selected by the Secure instance of ext-MPAMCFG\_PART\_SEL. MPAMCFG\_CPBM\_ns controls the cache portions for the Non-secure PARTID selected by the Non-secure instance of ext-MPAMCFG\_PART\_SEL.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offset
:   0x1000

Access type
:   RW

Reset value
:   0000 0000 0000 0000 0000 0000 1111 1111

### Bit descriptions

Figure 1. ext\_mpamcfg\_cpbm\_s bit assignments

![ext_mpamcfg_cpbm_s bit assignments](images/0293-MPAMCFG_CPBM_s-MPAM-Cache-Portion-Bitmap-Partition-Configuration-Register-for-Secure-PARTIDs-img01.svg)

<table id="zxj1733414942874__ampamcfg_cpbm_s-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMCFG_CPBM_s bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d327350e143" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d327350e146" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d327350e149" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d327350e152" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__31-9-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    S_EXCL
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Exclusive Secure CPBM enable. If set, all portions enabled in the Secure MPAMCFG_CPBM_s register will prevent corresponding portions enabled in the MPAMCFG_CPBM_ns register from taking effect.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Each set MPAMCFG_CPBM_s bit has no effect on the corresponding MPAMCFG_CPBM_ns bit.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Each set MPAMCFG_CPBM_s bit masks the corresponding MPAMCFG_CPBM_ns bit from taking effect.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__id-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CPBM7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Each bit, CPBM&lt;n&gt;, grants permission to the PARTID to allocate cache lines within cache portion n.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is not permitted to allocate into cache portion n.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is permitted to allocate within cache portion n.
      </p>
     </dd>
    </dl>
    <p>
     The number of bits in the cache portion partitioning bit map of this component is given in ext-MPAMF_CPOR_IDR.CPBM_WD.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__id-7-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CPBM6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Each bit, CPBM&lt;n&gt;, grants permission to the PARTID to allocate cache lines within cache portion n.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is not permitted to allocate into cache portion n.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is permitted to allocate within cache portion n.
      </p>
     </dd>
    </dl>
    <p>
     The number of bits in the cache portion partitioning bit map of this component is given in ext-MPAMF_CPOR_IDR.CPBM_WD.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__id-6-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CPBM5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Each bit, CPBM&lt;n&gt;, grants permission to the PARTID to allocate cache lines within cache portion n.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is not permitted to allocate into cache portion n.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is permitted to allocate within cache portion n.
      </p>
     </dd>
    </dl>
    <p>
     The number of bits in the cache portion partitioning bit map of this component is given in ext-MPAMF_CPOR_IDR.CPBM_WD.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__id-5-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CPBM4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Each bit, CPBM&lt;n&gt;, grants permission to the PARTID to allocate cache lines within cache portion n.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is not permitted to allocate into cache portion n.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is permitted to allocate within cache portion n.
      </p>
     </dd>
    </dl>
    <p>
     The number of bits in the cache portion partitioning bit map of this component is given in ext-MPAMF_CPOR_IDR.CPBM_WD.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__id-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CPBM3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Each bit, CPBM&lt;n&gt;, grants permission to the PARTID to allocate cache lines within cache portion n.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is not permitted to allocate into cache portion n.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is permitted to allocate within cache portion n.
      </p>
     </dd>
    </dl>
    <p>
     The number of bits in the cache portion partitioning bit map of this component is given in ext-MPAMF_CPOR_IDR.CPBM_WD.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__id-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CPBM2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Each bit, CPBM&lt;n&gt;, grants permission to the PARTID to allocate cache lines within cache portion n.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is not permitted to allocate into cache portion n.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is permitted to allocate within cache portion n.
      </p>
     </dd>
    </dl>
    <p>
     The number of bits in the cache portion partitioning bit map of this component is given in ext-MPAMF_CPOR_IDR.CPBM_WD.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__id-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CPBM1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Each bit, CPBM&lt;n&gt;, grants permission to the PARTID to allocate cache lines within cache portion n.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is not permitted to allocate into cache portion n.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is permitted to allocate within cache portion n.
      </p>
     </dd>
    </dl>
    <p>
     The number of bits in the cache portion partitioning bit map of this component is given in ext-MPAMF_CPOR_IDR.CPBM_WD.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="zxj1733414942874__id-1-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CPBM0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Each bit, CPBM&lt;n&gt;, grants permission to the PARTID to allocate cache lines within cache portion n.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is not permitted to allocate into cache portion n.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The PARTID is permitted to allocate within cache portion n.
      </p>
     </dd>
    </dl>
    <p>
     The number of bits in the cache portion partitioning bit map of this component is given in ext-MPAMF_CPOR_IDR.CPBM_WD.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="zxj1733414942874__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
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
   <th class="documents-nocellnorowborder" colspan="1" id="d327350e717" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d327350e720" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d327350e723" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d327350e726" rowspan="1">
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
    0x1000
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMCFG_CPBM_s
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
