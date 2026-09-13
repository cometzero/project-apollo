# CLUSTERROM_DEVARCH, Cluster ROM table Device Architecture Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary/CLUSTERROM-DEVARCH--Cluster-ROM-table-Device-Architecture-Register>

### CLUSTERROM\_DEVARCH, Cluster ROM table Device Architecture Register

Identifies the architect and architecture of a CoreSight component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERROM

Register offset
:   0xFBC

Access type
:   RO

Reset value
:   0100 0111 0111 0000 0000 1010 1111 0111

### Bit descriptions

Figure 1. ext\_clusterrom\_devarch bit assignments

![ext_clusterrom_devarch bit assignments](images/0534-CLUSTERROM_DEVARCH-Cluster-ROM-table-Device-Architecture-Register-img01.svg)

<table id="pmj1733415222717__aclusterrom_devarch-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERROM_DEVARCH bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d333491e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d333491e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d333491e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d333491e146" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:21]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ARCHITECT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Architect.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01000111011
      </span>
     </dt>
     <dd>
      <p>
       JEP106 continuation code 0x4, ID code 0x3B. Arm Limited.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pmj1733415222717__id-31-21-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b01000111011
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PRESENT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Present.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       DEVARCH information present.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pmj1733415222717__id-20-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    REVISION
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Revision.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Revision 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="pmj1733415222717__id-19-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [15:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ARCHID
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Architecture ID.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000101011110111
      </span>
     </dt>
     <dd>
      <p>
       ROM Table v0. The debug tool must inspect ext-CLUSTERROM_DEVTYPE and ext-CLUSTERROM_DEVID to determine further information about the ROM Table.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="pmj1733415222717__id-15-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x0AF7
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
