# PBX_FEAT_SPT1, Postbox Feature Support 1 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FEAT-SPT1--Postbox-Feature-Support-1-Register>

### PBX\_FEAT\_SPT1, Postbox Feature Support 1 Register

Returns information on supported MHU features

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   0x0014

### Bit descriptions

Figure 1. MHUS.PBX\_PBX\_FEAT\_SPT1 bit assignments

![mhus.pbx_pbx_feat_spt1 bit assignments](images/0103-PBX_FEAT_SPT1-Postbox-Feature-Support-1-Register-img01.svg)

<table id="mhus_pbx_pbx_feat_spt1__apbx_feat_spt1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PBX_FEAT_SPT1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d60514e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d60514e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d60514e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d60514e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:4]
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
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    AUTO_OP_SPT
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Auto Op Protocol support
    </p>
    <p>
     For more information about the Auto Op protocol, see the
     <a href="https://developer.arm.com/documentation/aes0072" target="_blank">
      <span>
       <cite>
        Message Handling Unit Architecture version 3.0
       </cite>
      </span>
     </a>
     .
    </p>
    <p>
     The value of this field is set for MHU-320AE:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Auto Op(Full) is implemented
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
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
   <th class="documents-nocellnorowborder" colspan="1" id="d60514e256" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d60514e259" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d60514e262" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d60514e265" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUS.PBX
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0014
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PBX_FEAT_SPT1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
