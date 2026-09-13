# CLUSTERAMU_AMPIDR2, Cluster Activity Monitors Peripheral Identification Register 2

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-AMU-registers-summary/CLUSTERAMU-AMPIDR2--Cluster-Activity-Monitors-Peripheral-Identification-Register-2>

### CLUSTERAMU\_AMPIDR2, Cluster Activity Monitors Peripheral Identification Register 2

Provides information to identify a Activity Monitor component.

### Configurations

This register is required for CoreSight compliance.

### Attributes

Width
:   32

Component
:   CLUSTERAMU

Register offset
:   0xFE8

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 1011
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusteramu\_ampidr2 bit assignments

![ext_clusteramu_ampidr2 bit assignments](images/0383-CLUSTERAMU_AMPIDR2-Cluster-Activity-Monitors-Peripheral-Identification-Register-2-img01.svg)

<table id="zod1733415025903__aclusteramu_ampidr2-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERAMU_AMPIDR2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d164369e144" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d164369e147" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d164369e150" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d164369e153" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="zod1733415025903__31-8-reset" rowspan="1">
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
     Component major revision.
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
   <td class="documents-cell-norowborder" colspan="1" id="zod1733415025903__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
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
     JEDEC assignee.
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
   <td class="documents-cell-norowborder" colspan="1" id="zod1733415025903__id-3-reset" rowspan="1">
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
     JEP106 identification code bits [6:4].
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
   </td>
   <td class="documents-cellrowborder" colspan="1" id="zod1733415025903__id-2-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b011
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
