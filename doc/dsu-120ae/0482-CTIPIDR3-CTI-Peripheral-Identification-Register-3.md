# CTIPIDR3, CTI Peripheral Identification Register 3

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR3--CTI-Peripheral-Identification-Register-3>

### CTIPIDR3, CTI Peripheral Identification Register 3

Provides information to identify a CTI component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0xFEC

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ctipidr3 bit assignments

![ext_ctipidr3 bit assignments](images/0482-CTIPIDR3-CTI-Peripheral-Identification-Register-3-img01.svg)

<table id="xcx1733415137071__actipidr3-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIPIDR3 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d358350e149" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d358350e152" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d358350e155" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d358350e158" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="xcx1733415137071__31-8-reset" rowspan="1">
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
    REVAND
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Component minor revision.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Component minor revision 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xcx1733415137071__id-7-4-reset" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      Cluster
     </dt>
     <dd>
      <span class="documents-g.number.bin">
       0b0000
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
    CMOD
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Customer Modified.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       The component is not modified from the original design.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="xcx1733415137071__id-3-0-reset" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      Cluster
     </dt>
     <dd>
      <span class="documents-g.number.bin">
       0b0000
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
   <th class="documents-nocellnorowborder" colspan="1" id="d358350e350" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d358350e353" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d358350e356" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d358350e359" rowspan="1">
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
    0xFEC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIPIDR3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
