# SRAS_ERR<n>MISC1, Error Record <n> Miscellaneous Register 1, n = 0 - 3

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary/SRAS-ERR-n-MISC1--Error-Record--n--Miscellaneous-Register-1--n---0---3>

### SRAS\_ERR<n>MISC1, Error Record <n> Miscellaneous Register 1, n = 0 - 3

Records additional information on reported error.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   MHUS.SRAS

Register offset
:   (64 \* n) + 0x0028

### Bit descriptions

Figure 1. MHUS\_SRAS\_ERR<n>MISC1 bit assignments

![mhus_sras_err_n_misc1 bit assignments](images/0150-SRAS_ERR-n-MISC1-Error-Record-n-Miscellaneous-Register-1-n-0-3-img01.svg)

<table id="mhus_sras_err_n_misc1__asras_errnmisc1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SRAS_ERR&lt;n&gt;MISC1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d52446e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d52446e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d52446e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d52446e160" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
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
    DATA
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Additional information on recorded error. See
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability?lang=en" title="MHU-320AE uses a range of configurable RAS features for all RAMs, which include Single Error Correction and Double Error Detection (SECDED), and scrub, software and bus error reporting.">
      Reliability, Accessibility, and Serviceability
     </a>
     , for more information.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Accessibility
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
   <th class="documents-nocellnorowborder" colspan="1" id="d52446e245" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d52446e248" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d52446e251" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d52446e254" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUS.SRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    (64 * n) + 0x0028
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SRAS_ERR&lt;n&gt;MISC1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
