# MBX_BLK_ID, Mailbox Block Identifier Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-BLK-ID--Mailbox-Block-Identifier-Register>

### MBX\_BLK\_ID, Mailbox Block Identifier Register

Identifies the block as a Mailbox.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   0x0000

### Bit descriptions

Figure 1. MHUR.MBX\_MBX\_BLK\_ID bit assignments

![mhur.mbx_mbx_blk_id bit assignments](images/0195-MBX_BLK_ID-Mailbox-Block-Identifier-Register-img01.svg)

<table id="mhur_mbx_mbx_blk_id__ambx_blk_id-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MBX_BLK_ID bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d62840e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d62840e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d62840e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d62840e160" rowspan="1">
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
    BLK_ID
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Block Identifier
    </p>
    <p>
     Identifies the block as a Mailbox
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Mailbox
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
   <th class="documents-nocellnorowborder" colspan="1" id="d62840e247" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d62840e250" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d62840e253" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d62840e256" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.MBX
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0000
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_BLK_ID
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
