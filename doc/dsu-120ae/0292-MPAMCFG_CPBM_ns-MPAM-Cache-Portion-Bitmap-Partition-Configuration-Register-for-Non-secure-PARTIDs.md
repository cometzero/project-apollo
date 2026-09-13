# MPAMCFG_CPBM_ns, MPAM Cache Portion Bitmap Partition Configuration Register for Non-secure PARTIDs

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMCFG-CPBM-ns--MPAM-Cache-Portion-Bitmap-Partition-Configuration-Register-for-Non-secure-PARTIDs>

### MPAMCFG\_CPBM\_ns, MPAM Cache Portion Bitmap Partition Configuration Register for Non-secure PARTIDs

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

Figure 1. ext\_mpamcfg\_cpbm\_ns bit assignments

![ext_mpamcfg_cpbm_ns bit assignments](images/0292-MPAMCFG_CPBM_ns-MPAM-Cache-Portion-Bitmap-Partition-Configuration-Register-for-Non-secure-PARTIDs-img01.svg)

<table id="oam1733414941422__ampamcfg_cpbm_ns-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMCFG_CPBM_ns bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d360629e143" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d360629e146" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d360629e149" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d360629e152" rowspan="1">
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
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="oam1733414941422__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
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
   <td class="documents-cell-norowborder" colspan="1" id="oam1733414941422__id-7-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oam1733414941422__id-6-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oam1733414941422__id-5-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oam1733414941422__id-4-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oam1733414941422__id-3-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oam1733414941422__id-2-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="oam1733414941422__id-1-reset" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="oam1733414941422__id-0-reset" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d360629e663" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d360629e666" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d360629e669" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d360629e672" rowspan="1">
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
    MPAMCFG_CPBM_ns
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
