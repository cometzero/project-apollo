# MBX_PIDR2, Mailbox Peripheral ID 2 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR2--Mailbox-Peripheral-ID-2-Register>

### MBX\_PIDR2, Mailbox Peripheral ID 2 Register

Returns byte[2] of the peripheral ID for Mailbox page.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   0x0FE8

### Bit descriptions

Figure 1. MHUR.MBX\_MBX\_PIDR2 bit assignments

![mhur.mbx_mbx_pidr2 bit assignments](images/0216-MBX_PIDR2-Mailbox-Peripheral-ID-2-Register-img01.svg)

<table id="mhur_mbx_mbx_pidr2__ambx_pidr2-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MBX_PIDR2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d28475e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d28475e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d28475e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d28475e160" rowspan="1">
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
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    REVISION
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The REVISION field is an incremental value starting at
     <span class="documents-g.number.hex">
      0x0
     </span>
     for the first design of a component.
    </p>
    <p>
     The value is increased by 1 for both major and minor revisions and is used as a look-up to establish the exact major and minor revision.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The reset value depends on the product version used.
    <ul>
     <li>
      <span class="documents-g.number.hex">
       0x0
      </span>
      - r0p0
     </li>
     <li>
      <span class="documents-g.number.hex">
       0x1
      </span>
      - r0p1
     </li>
    </ul>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    JEDEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Must be
     <span class="documents-g.number.bin">
      0b1
     </span>
     to indicate that a JEDEC-assigned value is used.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [2:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    DES_1
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     JEP106 identification bits [6:4]
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b011
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
   <th class="documents-nocellnorowborder" colspan="1" id="d28475e325" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d28475e328" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d28475e331" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d28475e334" rowspan="1">
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
    0x0FE8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_PIDR2
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
