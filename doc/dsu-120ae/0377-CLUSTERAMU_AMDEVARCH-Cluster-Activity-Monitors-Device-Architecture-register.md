# CLUSTERAMU_AMDEVARCH, Cluster Activity Monitors Device Architecture register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMDEVARCH--Cluster-Activity-Monitors-Device-Architecture-register>

### CLUSTERAMU\_AMDEVARCH, Cluster Activity Monitors Device Architecture register

Identifies the programmers' model architecture of the Activity Monitor component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERAMU

Register offset
:   0xFBC

Access type
:   RO

Reset value
:   0100 0111 0111 0000 0000 1010 0110 0110

### Bit descriptions

Figure 1. ext\_clusteramu\_amdevarch bit assignments

![ext_clusteramu_amdevarch bit assignments](images/0377-CLUSTERAMU_AMDEVARCH-Cluster-Activity-Monitors-Device-Architecture-register-img01.svg)

<table id="vhq1733415020113__aclusteramu_amdevarch-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMDEVARCH bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d294023e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d294023e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d294023e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d294023e146" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="vhq1733415020113__id-31-21-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="vhq1733415020113__id-20-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="vhq1733415020113__id-19-16-reset" rowspan="1">
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
       0b0000101001100110
      </span>
     </dt>
     <dd>
      <p>
       Activity Monitor (AMU) architecture AMUv1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="vhq1733415020113__id-15-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x0A66
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
