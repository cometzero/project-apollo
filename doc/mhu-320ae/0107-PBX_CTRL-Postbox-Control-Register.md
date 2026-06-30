# PBX_CTRL, Postbox Control Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-CTRL--Postbox-Control-Register>

### PBX\_CTRL, Postbox Control Register

This register contains control bits for the postbox

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   0x0100

### Bit descriptions

Figure 1. MHUS.PBX\_PBX\_CTRL bit assignments

![mhus.pbx_pbx_ctrl bit assignments](images/0107-PBX_CTRL-Postbox-Control-Register-img01.svg)

<table id="mhus_pbx_pbx_ctrl__apbx_ctrl-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PBX_CTRL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d94153e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d94153e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d94153e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d94153e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:2]
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CH_OP_MSK
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Channel Operational Mask
    </p>
    <p>
     Controls whether Channels need to be idle to allow a controlled entry into a non-operational state
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Channels must be idle to enter a non-operational state
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Channels status is ignored when considering entry into a non-operational state
      </p>
     </dd>
    </dl>
    <p>
     This field has no effect on entry into a non-operation state in an uncontrolled manner
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    OP_REQ
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Operational Request
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Postbox is not requested to remain in the operational state
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Postbox is requested to remain in the operational state
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d94153e310" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d94153e313" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d94153e316" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d94153e319" rowspan="1">
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
    0x0100
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PBX_CTRL
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
