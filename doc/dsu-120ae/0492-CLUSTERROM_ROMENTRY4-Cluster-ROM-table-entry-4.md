# CLUSTERROM_ROMENTRY4, Cluster ROM table entry 4

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary/CLUSTERROM-ROMENTRY4--Cluster-ROM-table-entry-4>

### CLUSTERROM\_ROMENTRY4, Cluster ROM table entry 4

Provides the address offset for one CoreSight component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERROM

Register offset
:   0x010

Access type
:   RO

### Bit descriptions

When NUM\_CORES >= 3

Figure 1. ext\_clusterrom\_romentry4 bit assignments

![ext_clusterrom_romentry4 bit assignments](images/0492-CLUSTERROM_ROMENTRY4-Cluster-ROM-table-entry-4-img01.svg)

<table id="ldy1733415149538__aclusterrom_romentry4-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERROM_ROMENTRY4 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d281303e132" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d281303e135" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d281303e138" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d281303e141" rowspan="1">
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
       0b00000000000101110000
      </span>
     </dt>
     <dd>
      <p>
       Core 2 ROM table at address 0x18_0000 in the Cluster Debug APB address map.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ldy1733415149538__id-31-12-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00170
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
   <td class="documents-cell-norowborder" colspan="1" id="ldy1733415149538__11-9-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="ldy1733415149538__id-8-4-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="ldy1733415149538__3-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="ldy1733415149538__id-2-reset" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="ldy1733415149538__id-1-0-reset" rowspan="1">
    <span>
     xx
    </span>
   </td>
  </tr>
 </tbody>
</table>

When NUM\_CORES < 3

Figure 2. ext\_clusterrom\_romentry4 bit assignments

![ext_clusterrom_romentry4 bit assignments](images/0492-CLUSTERROM_ROMENTRY4-Cluster-ROM-table-entry-4-img02.svg)

<table id="ldy1733415149538__aclusterrom_romentry4-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   CLUSTERROM_ROMENTRY4 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d281303e476" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d281303e479" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d281303e482" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d281303e485" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="ldy1733415149538__31-0-reset" rowspan="1">
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
