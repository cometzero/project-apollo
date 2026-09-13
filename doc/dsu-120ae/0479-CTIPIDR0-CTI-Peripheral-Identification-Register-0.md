# CTIPIDR0, CTI Peripheral Identification Register 0

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIPIDR0--CTI-Peripheral-Identification-Register-0>

### CTIPIDR0, CTI Peripheral Identification Register 0

Provides information to identify a CTI component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0xFE0

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 1110 1100
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ctipidr0 bit assignments

![ext_ctipidr0 bit assignments](images/0479-CTIPIDR0-CTI-Peripheral-Identification-Register-0-img01.svg)

<table id="kff1733415134301__actipidr0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIPIDR0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d60959e149" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d60959e152" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d60959e155" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d60959e158" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="kff1733415134301__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PART_0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Part number bits [7:0].
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11101100
      </span>
     </dt>
     <dd>
      <p>
       DSU-120AE Cross Trigger Interface. Bits [7:0] of part number 0x4EC.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="kff1733415134301__id-7-0-reset" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      Cluster
     </dt>
     <dd>
      <span class="documents-g.number.hex">
       0xEC
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
   <th class="documents-nocellnorowborder" colspan="1" id="d60959e281" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d60959e284" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d60959e287" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d60959e290" rowspan="1">
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
    0xFE0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIPIDR0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
