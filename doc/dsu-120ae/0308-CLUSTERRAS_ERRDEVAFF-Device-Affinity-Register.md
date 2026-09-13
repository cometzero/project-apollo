# CLUSTERRAS_ERRDEVAFF, Device Affinity Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRDEVAFF--Device-Affinity-Register>

### CLUSTERRAS\_ERRDEVAFF, Device Affinity Register

ERRDEVAFF is a copy of part of AArch64-MPIDR\_EL1.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   CLUSTERRAS

Register offset
:   0xFA8

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx 00xx xxx0 xxxx xxxx 1000 0000 0000 0000
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_errdevaff bit assignments

![ext_clusterras_errdevaff bit assignments](images/0308-CLUSTERRAS_ERRDEVAFF-Device-Affinity-Register-img01.svg)

<table id="cdw1733414947888__aclusterras_errdevaff-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERRDEVAFF bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d58430e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d58430e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d58430e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d58430e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:40]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cdw1733414947888__63-40-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [39:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Aff3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Affinity level 3. The AArch64-MPIDR_EL1.Aff3 field, viewed from the highest Exception level of the associated PE or PEs.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cdw1733414947888__id-39-32-reset" rowspan="1">
    <code>
     8{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    F0V
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates that the ERRDEVAFF.Aff0 field is valid.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ERRDEVAFF.Aff0 is not valid, and the PE affinity level is 1, 2 or 3.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cdw1733414947888__id-31-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    U
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uniprocessor. The AArch64-MPIDR_EL1.U bit viewed from the highest Exception level of the associated PE.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The PE is part of a multiprocessor system.
      </p>
     </dd>
    </dl>
    <p>
     If ERRDEVAFF.Aff0 is not valid, this bit is not valid and reads as
     <span class="documents-archterm">
      UNKNOWN
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cdw1733414947888__id-30-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [29:25]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cdw1733414947888__29-25-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Multithreaded. The AArch64-MPIDR_EL1.MT bit viewed from the highest Exception level of the associated PE.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Performance of PEs at the lowest affinity level is largely independent.
      </p>
     </dd>
    </dl>
    <p>
     If ERRDEVAFF.Aff0 is not valid, this bit is not valid and reads as
     <span class="documents-archterm">
      UNKNOWN
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cdw1733414947888__id-24-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Aff2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Affinity level 2.
    </p>
    <p>
     This field is the AArch64-MPIDR_EL1.Aff2 field viewed from the highest Exception level of the associated PE or PEs.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cdw1733414947888__id-23-16-reset" rowspan="1">
    <code>
     8{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Aff1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Affinity level 1.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10000000
      </span>
     </dt>
     <dd>
      <p>
       ERRDEVAFF.Aff2 is valid, and the PE affinity level is 2.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cdw1733414947888__id-15-8-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x80
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Aff0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Affinity level 0.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000
      </span>
     </dt>
     <dd>
      <p>
       The PE affinity is above level 1 or a subset of level 1.
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="cdw1733414947888__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
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
   <th class="documents-nocellnorowborder" colspan="1" id="d58430e479" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d58430e482" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d58430e485" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d58430e488" rowspan="1">
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
    0xFA8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERRDEVAFF
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
