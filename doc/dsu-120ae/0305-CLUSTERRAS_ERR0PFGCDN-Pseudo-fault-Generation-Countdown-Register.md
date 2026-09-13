# CLUSTERRAS_ERR0PFGCDN, Pseudo-fault Generation Countdown Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0PFGCDN--Pseudo-fault-Generation-Countdown-Register>

### CLUSTERRAS\_ERR0PFGCDN, Pseudo-fault Generation Countdown Register

Generates one of the errors enabled in the corresponding ext-CLUSTERRAS\_ERR0PFGCTL register.

### Configurations

External register CLUSTERRAS\_ERR0PFGCDN bits [63:0] are architecturally mapped to AArch64 System register [ERXPFGCDN\_EL1, Selected Pseudo-fault Generation Countdown Register](/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXPFGCDN-EL1--Selected-Pseudo-fault-Generation-Countdown-Register?lang=en "Accesses the ext-CLUSTERRAS_ERR0PFGCDN register when the value in AArch64-ERRSELR_EL1.SEL is set to 0.") bits [63:0].

### Attributes

Width
:   64

Component
:   CLUSTERRAS

Register offset
:   0x810

Access type
:   RW

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_err0pfgcdn bit assignments

![ext_clusterras_err0pfgcdn bit assignments](images/0305-CLUSTERRAS_ERR0PFGCDN-Pseudo-fault-Generation-Countdown-Register-img01.svg)

<table id="tzv1733414911873__aclusterras_err0pfgcdn-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERR0PFGCDN bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d272665e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d272665e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d272665e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d272665e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="tzv1733414911873__63-32-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [31:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CDN
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Countdown value.
    </p>
    <p>
     This field is copied to Error Generation Counter when either:
    </p>
    <ul>
     <li>
      Software writes ext-CLUSTERRAS_ERR0PFGCTL.CDNEN with 1.
     </li>
     <li>
      The Error Generation Counter decrements to zero and ext-CLUSTERRAS_ERR0PFGCTL.R == 1.
     </li>
    </ul>
    <p>
     While ext-CLUSTERRAS_ERR0PFGCTL.CDNEN == 1 and the Error Generation Counter is nonzero, the counter decrements by 1 for each cycle. When the counter reaches 0, one of the errors enabled in the ext-CLUSTERRAS_ERR0PFGCTL register is generated.
    </p>
    <div class="documents-p">
     <blockquote title="Note info">
      <h3 class="documents-underline">
       Note
      </h3>
      The current Error Generation Counter value is not visible to software.
     </blockquote>
    </div>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="tzv1733414911873__id-31-0-reset" rowspan="1">
    <code>
     32{x}
    </code>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d272665e251" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d272665e254" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d272665e257" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d272665e260" rowspan="1">
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
    0x810
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERR0PFGCDN
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
