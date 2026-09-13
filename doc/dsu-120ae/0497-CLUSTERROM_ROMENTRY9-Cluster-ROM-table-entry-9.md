# CLUSTERROM_ROMENTRY9, Cluster ROM table entry 9

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary/CLUSTERROM-ROMENTRY9--Cluster-ROM-table-entry-9>

### CLUSTERROM\_ROMENTRY9, Cluster ROM table entry 9

Provides the address offset for one CoreSight component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERROM

Register offset
:   0x024

Access type
:   RO

### Bit descriptions

When NUM\_CORES >= 8

Figure 1. ext\_clusterrom\_romentry9 bit assignments

![ext_clusterrom_romentry9 bit assignments](images/0497-CLUSTERROM_ROMENTRY9-Cluster-ROM-table-entry-9-img01.svg)

<table id="pyz1733415159225__aclusterrom_romentry9-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERROM_ROMENTRY9 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d172607e132" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d172607e135" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d172607e138" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d172607e141" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OFFSET
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The component address, relative to the base address of this ROM Table. The component address is calculated using the following equation:
    </p>
    <p>
     Component Address = ROM Table Base Address + (OFFSET &lt;&lt; 12).
    </p>
    <p>
     The value of this field depends on the cluster configuration.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000001111110000
      </span>
     </dt>
     <dd>
      <p>
       Core 7 ROM table at address 0x40_0000 in the Cluster Debug APB address map.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pyz1733415159225__id-31-12-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x003F0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11:9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pyz1733415159225__11-9-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    POWERID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The power domain ID of the component. This field is only valid if the POWERIDVALID field is
     <span class="documents-g.number.bin">
      0b1
     </span>
     .
    </p>
    <p>
     The value of this field depends on the cluster configuration.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX0 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX1 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00010
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX2 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00011
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX3 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00100
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX4 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00101
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX5 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00110
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX6 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00111
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX7 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01000
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX8 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01001
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX9 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01010
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX10 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01011
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX11 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01100
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX12 power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01101
      </span>
     </dt>
     <dd>
      <p>
       PDCOMPLEX13 power domain.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pyz1733415159225__id-8-4-reset" rowspan="1">
    <code>
     5{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pyz1733415159225__3-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    POWERIDVALID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if the Power domain ID field contains a Power domain ID.
    </p>
    <p>
     The value of this field depends on the cluster configuration.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       A power domain ID is not provided.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The POWERID field provides a power domain ID.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pyz1733415159225__id-2-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [1:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PRESENT
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Indicates whether an entry is present at this location in the ROM Table.
    </p>
    <p>
     The value of this field depends on the cluster configuration.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       The ROM entry is not present and this is the final entry in the ROM table.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       The ROM entry is not present and this is not the final entry in the ROM table.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       The ROM entry is present.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="pyz1733415159225__id-1-0-reset" rowspan="1">
    <span>
     xx
    </span>
   </td>
  </tr>
 </tbody>
</table>

When NUM\_CORES < 8

Figure 2. ext\_clusterrom\_romentry9 bit assignments

![ext_clusterrom_romentry9 bit assignments](images/0497-CLUSTERROM_ROMENTRY9-Cluster-ROM-table-entry-9-img02.svg)

<table id="pyz1733415159225__aclusterrom_romentry9-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   CLUSTERROM_ROMENTRY9 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d172607e476" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d172607e479" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d172607e482" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d172607e485" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [31:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cellrowborder" colspan="1" id="pyz1733415159225__31-0-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
