# CLUSTERRAS_ERR0MISC3, Error Record Miscellaneous Register 3

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0MISC3--Error-Record-Miscellaneous-Register-3>

### CLUSTERRAS\_ERR0MISC3, Error Record Miscellaneous Register 3

Unimplemented error syndrome register.

### Configurations

External register CLUSTERRAS\_ERR0MISC3 bits [63:0] are architecturally mapped to AArch64 System register [ERXMISC3\_EL1, Selected Error Record Miscellaneous Register 3](/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXMISC3-EL1--Selected-Error-Record-Miscellaneous-Register-3?lang=en "Accesses ext-CLUSTERRAS_ERR0MISC3 when the value in AArch64-ERRSELR_EL1.SEL is set to 0.") bits [63:0].

### Attributes

Width
:   64

Component
:   CLUSTERRAS

Register offset
:   0x038

Access type
:   RW

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_clusterras\_err0misc3 bit assignments

![ext_clusterras_err0misc3 bit assignments](images/0302-CLUSTERRAS_ERR0MISC3-Error-Record-Miscellaneous-Register-3-img01.svg)

<table id="qiz1733414920743__aclusterras_err0misc3-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERR0MISC3 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d350776e147" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d350776e150" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d350776e153" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d350776e156" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [63:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cellrowborder" colspan="1" id="qiz1733414920743__63-0-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
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
   <th class="documents-nocellnorowborder" colspan="1" id="d350776e210" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d350776e213" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d350776e216" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d350776e219" rowspan="1">
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
    0x038
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERR0MISC3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
