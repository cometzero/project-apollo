# CTIPIDR1, CTI Peripheral Identification Register 1

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR1--CTI-Peripheral-Identification-Register-1>

### CTIPIDR1, CTI Peripheral Identification Register 1

Provides information to identify a CTI component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0xFE4

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 1011 0100
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ctipidr1 bit assignments

![ext_ctipidr1 bit assignments](images/0480-CTIPIDR1-CTI-Peripheral-Identification-Register-1-img01.svg)

<table id="wtr1733415135311__actipidr1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIPIDR1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d313018e149" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d313018e152" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d313018e155" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d313018e158" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="wtr1733415135311__31-8-reset" rowspan="1">
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
    DES_0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     JEP106 identification code bits [3:0].
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1011
      </span>
     </dt>
     <dd>
      <p>
       Arm Limited. Bits [3:0] of JEP106 identification code 0x3B.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wtr1733415135311__id-7-4-reset" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      Cluster
     </dt>
     <dd>
      <span class="documents-g.number.bin">
       0b1011
      </span>
     </dd>
     <dt class="documents-dlterm">
      Core
     </dt>
     <dd>
      See section
      <cite>
       CTI register identification values
      </cite>
      in chapter
      <cite>
       Debug
      </cite>
      in your core
      <cite>
       Technical Reference Manual
      </cite>
      for this value.
     </dd>
    </dl>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PART_1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Part number bits [11:8].
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       DSU-120AE Cross Trigger Interface. Bits [11:8] of part number 0x4EC.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="wtr1733415135311__id-3-0-reset" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      Cluster
     </dt>
     <dd>
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dd>
     <dt class="documents-dlterm">
      Core
     </dt>
     <dd>
      See section
      <cite>
       CTI register identification values
      </cite>
      in chapter
      <cite>
       Debug
      </cite>
      in your core
      <cite>
       Technical Reference Manual
      </cite>
      for this value.
     </dd>
    </dl>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d313018e350" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d313018e353" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d313018e356" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d313018e359" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFE4
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIPIDR1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
