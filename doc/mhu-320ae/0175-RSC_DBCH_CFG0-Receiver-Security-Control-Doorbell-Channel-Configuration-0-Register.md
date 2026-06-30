# RSC_DBCH_CFG0, Receiver Security Control Doorbell Channel Configuration 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Security-Control-register-summary/RSC-DBCH-CFG0--Receiver-Security-Control-Doorbell-Channel-Configuration-0-Register>

### RSC\_DBCH\_CFG0, Receiver Security Control Doorbell Channel Configuration 0 Register

Returns doorbell channel configuration information

### Configurations

This register is present only when TZE is implemented for the MHUR and DBE is implemented. Otherwise, direct accesses to RSC\_DBCH\_CFG0 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.RSC

Register offset
:   0x0020

### Bit descriptions

Figure 1. MHUR.RSC\_RSC\_DBCH\_CFG0 bit assignments

![mhur.rsc_rsc_dbch_cfg0 bit assignments](images/0175-RSC_DBCH_CFG0-Receiver-Security-Control-Doorbell-Channel-Configuration-0-Register-img01.svg)

<table id="mhur_rsc_rsc_dbch_cfg0__arsc_dbch_cfg0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RSC_DBCH_CFG0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d128945e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d128945e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d128945e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d128945e163" rowspan="1">
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
    <code id="mhur_rsc_rsc_dbch_cfg0__bits-7-0-reset">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d128945e253" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d128945e256" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d128945e259" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d128945e262" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.RSC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0020
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RSC_DBCH_CFG0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
