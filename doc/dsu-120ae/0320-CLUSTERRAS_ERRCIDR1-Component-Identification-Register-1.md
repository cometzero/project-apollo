# CLUSTERRAS_ERRCIDR1, Component Identification Register 1

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR1--Component-Identification-Register-1>

### CLUSTERRAS\_ERRCIDR1, Component Identification Register 1

Provides discovery information for the component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERRAS

Register offset
:   0xFF4

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 1111 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_errcidr1 bit assignments

![ext_clusterras_errcidr1 bit assignments](images/0320-CLUSTERRAS_ERRCIDR1-Component-Identification-Register-1-img01.svg)

<table id="cko1733414958838__aclusterras_errcidr1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERRCIDR1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d216060e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d216060e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d216060e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d216060e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="cko1733414958838__31-8-reset" rowspan="1">
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
    CLASS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Component class.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1111
      </span>
     </dt>
     <dd>
      <p>
       System component with no standardized register layout.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="cko1733414958838__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1111
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PRMBL_1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Component identification preamble, segment 1. This field reads as
     <span class="documents-g.number.hex">
      0x0
     </span>
     .
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="cko1733414958838__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
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
   <th class="documents-nocellnorowborder" colspan="1" id="d216060e267" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d216060e270" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d216060e273" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d216060e276" rowspan="1">
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
    0xFF4
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERRCIDR1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
