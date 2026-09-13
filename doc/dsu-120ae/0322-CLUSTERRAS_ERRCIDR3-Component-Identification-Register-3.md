# CLUSTERRAS_ERRCIDR3, Component Identification Register 3

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERRCIDR3--Component-Identification-Register-3>

### CLUSTERRAS\_ERRCIDR3, Component Identification Register 3

Provides discovery information for the component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERRAS

Register offset
:   0xFFC

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 1011 0001
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_errcidr3 bit assignments

![ext_clusterras_errcidr3 bit assignments](images/0322-CLUSTERRAS_ERRCIDR3-Component-Identification-Register-3-img01.svg)

<table id="itu1733414961029__aclusterras_errcidr3-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERRCIDR3 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d13541e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d13541e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d13541e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d13541e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="itu1733414961029__31-8-reset" rowspan="1">
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
    PRMBL_3
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Component identification preamble, segment 3. This field reads as
     <span class="documents-g.number.hex">
      0xB1
     </span>
     .
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="itu1733414961029__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0xB1
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
   <th class="documents-nocellnorowborder" colspan="1" id="d13541e228" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d13541e231" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d13541e234" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d13541e237" rowspan="1">
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
    0xFFC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERRCIDR3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
