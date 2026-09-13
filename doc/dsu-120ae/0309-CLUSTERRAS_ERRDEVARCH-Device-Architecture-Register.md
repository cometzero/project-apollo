# CLUSTERRAS_ERRDEVARCH, Device Architecture Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRDEVARCH--Device-Architecture-Register>

### CLUSTERRAS\_ERRDEVARCH, Device Architecture Register

Provides discovery information for the component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERRAS

Register offset
:   0xFBC

Access type
:   RO

Reset value
:   0100 0111 0111 0001 0000 1010 0000 0000

### Bit descriptions

Figure 1. ext\_clusterras\_errdevarch bit assignments

![ext_clusterras_errdevarch bit assignments](images/0309-CLUSTERRAS_ERRDEVARCH-Device-Architecture-Register-img01.svg)

<table id="ady1733414948808__aclusterras_errdevarch-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERRDEVARCH bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d116790e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116790e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116790e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d116790e146" rowspan="1">
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
    <p>
     Defines the architect of the component. Bits [31:28] are the JEP106 continuation code (JEP106 bank ID, minus 1) and bits [27:21] are the JEP106 ID code.
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
   <td class="documents-cell-norowborder" colspan="1" id="ady1733414948808__id-31-21-reset" rowspan="1">
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
     DEVARCH Present.
    </p>
    <p>
     Defines that the DEVARCH register is present.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Device Architecture information present.
      </p>
     </dd>
    </dl>
    <p>
     This bit is
     <span class="documents-archterm">
      RAO
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ady1733414948808__id-20-reset" rowspan="1">
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
    <p>
     Defines the architecture revision of the component. The defined values of this field are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       RAS System Architecture v1.1
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ady1733414948808__id-19-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ARCHVER
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Architecture Version.
    </p>
    <p>
     Defines the architecture version of the component. The defined values of this field are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       RAS System Architecture v1.
      </p>
     </dd>
    </dl>
    <p>
     This field reads as
     <span class="documents-g.number.bin">
      0b0000
     </span>
     .
    </p>
    <p>
     All other values are reserved.
    </p>
    <p>
     ARCHVER and ARCHPART are also defined as a single field, ARCHID, so that ARCHVER is ARCHID[15:12].
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ady1733414948808__id-15-12-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [11:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ARCHPART
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Architecture Part.
    </p>
    <p>
     Defines the architecture of the component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101000000000
      </span>
     </dt>
     <dd>
      <p>
       RAS system architecture.
      </p>
     </dd>
    </dl>
    <p>
     This register reads as
     <span class="documents-g.number.hex">
      0xA00
     </span>
     .
    </p>
    <p>
     ARCHVER and ARCHPART are also defined as a single field, ARCHID, so that ARCHPART is ARCHID[11:0].
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="ady1733414948808__id-11-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0xA00
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
   <th class="documents-nocellnorowborder" colspan="1" id="d116790e355" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116790e358" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d116790e361" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d116790e364" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFBC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERRDEVARCH
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
