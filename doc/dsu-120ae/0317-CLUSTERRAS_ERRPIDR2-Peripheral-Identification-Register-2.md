# CLUSTERRAS_ERRPIDR2, Peripheral Identification Register 2

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRPIDR2--Peripheral-Identification-Register-2>

### CLUSTERRAS\_ERRPIDR2, Peripheral Identification Register 2

Provides discovery information about the component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERRAS

Register offset
:   0xFE8

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0001 1011
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_errpidr2 bit assignments

![ext_clusterras_errpidr2 bit assignments](images/0317-CLUSTERRAS_ERRPIDR2-Peripheral-Identification-Register-2-img01.svg)

<table id="use1733414956055__aclusterras_errpidr2-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERRPIDR2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d175894e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d175894e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d175894e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d175894e150" rowspan="1">
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
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="use1733414956055__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    REVISION
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Component major revision. This field and ext-ERRPIDR3.REVAND together form the revision number of the component, with REVISION being the most significant part and REVAND the least significant part.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Component major revision 0.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Component major revision 1.
      </p>
     </dd>
    </dl>
    <p>
     For DSU-120AE:
    </p>
    <ul>
     <li>
      <p>
       Major revision 0 corresponds to r0p0.
      </p>
     </li>
     <li>
      <p>
       Major revision 1 corresponds to r0p1.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="use1733414956055__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    JEDEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     JEDEC-assigned JEP106 implementer code is used. This bit is
     <span class="documents-archterm">
      RAO
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       JEDEC-assignee values is used.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="use1733414956055__id-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [2:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    DES_1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Designer, JEP106 identification code, bits [6:4]. ext-ERRPIDR1.DES_0 and this field together form the JEDEC-assigned JEP106 identification code for the designer of the component.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       Arm Limited. Bits [6:4] of JEP106 identification code 0x3B.
      </p>
     </dd>
    </dl>
    <div class="documents-p">
     <blockquote title="Note info">
      <h3 class="documents-underline">
       Note
      </h3>
      For a component designed by Arm Limited, the JEP106 identification code is
      <span class="documents-g.number.hex">
       0x3B
      </span>
      .
     </blockquote>
    </div>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="use1733414956055__id-2-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b011
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
   <th class="documents-nocellnorowborder" colspan="1" id="d175894e345" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d175894e348" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d175894e351" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d175894e354" rowspan="1">
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
    0xFE8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERRPIDR2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
