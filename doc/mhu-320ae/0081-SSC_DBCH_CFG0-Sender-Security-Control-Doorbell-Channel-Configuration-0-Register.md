# SSC_DBCH_CFG0, Sender Security Control Doorbell Channel Configuration 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Security-Control-register-summary/SSC-DBCH-CFG0--Sender-Security-Control-Doorbell-Channel-Configuration-0-Register>

### SSC\_DBCH\_CFG0, Sender Security Control Doorbell Channel Configuration 0 Register

Returns doorbell channel configuration information

### Configurations

This register is present only when TZE is implemented for the MHUS and DBE is implemented. Otherwise, direct accesses to SSC\_DBCH\_CFG0 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.SSC

Register offset
:   0x0020

### Bit descriptions

Figure 1. MHUS.SSC\_SSC\_DBCH\_CFG0 bit assignments

![mhus.ssc_ssc_dbch_cfg0 bit assignments](images/0081-SSC_DBCH_CFG0-Sender-Security-Control-Doorbell-Channel-Configuration-0-Register-img01.svg)

<table id="mhus_ssc_ssc_dbch_cfg0__assc_dbch_cfg0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SSC_DBCH_CFG0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d8490e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d8490e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d8490e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d8490e163" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
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
    NUM_DBCH
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of Doorbell Channels
    </p>
    <dl>
     <dt class="documents-dlterm">
      0b00000000..0b01111111
     </dt>
     <dd>
      Number of DBCH is N+1, where N is the value of this field
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mhus_ssc_ssc_dbch_cfg0__bits-7-0-reset">
     8{x}
    </code>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d8490e253" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d8490e256" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d8490e259" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d8490e262" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUS.SSC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SSC_DBCH_CFG0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
