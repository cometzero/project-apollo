# MBX_PIDR3, Mailbox Peripheral ID 3 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-PIDR3--Mailbox-Peripheral-ID-3-Register>

### MBX\_PIDR3, Mailbox Peripheral ID 3 Register

Returns byte[3] of the peripheral ID for Mailbox page.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   0x0FEC

### Bit descriptions

Figure 1. MHUR.MBX\_MBX\_PIDR3 bit assignments

![mhur.mbx_mbx_pidr3 bit assignments](images/0217-MBX_PIDR3-Mailbox-Peripheral-ID-3-Register-img01.svg)

<table id="mhur_mbx_mbx_pidr3__ambx_pidr3-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MBX_PIDR3 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d7324e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7324e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7324e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d7324e160" rowspan="1">
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
    REVAND
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The REVAND field indicates minor errata fixes specific to this design, for example metal fixes after implementation. Usually this field is zero.
    </p>
    <p>
     Together with PIDR2.REVISION, PIDR3.REVAND forms the revision number of the component.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span id="mhur_mbx_mbx_pidr3__bits-7-4-reset-13">
     0x0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CMOD
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Customer Modified.
    </p>
    <p>
     If the component is reusable IP, the CMOD field indicates whether the customer has modified the behavior of the component.
    </p>
    <p>
     Arm recommends that the user or debugger reads the documentation for the
    </p>
    <p>
     component to determine the modifications that are made to the component.
    </p>
    <p>
     For any two components with the same values of the Peripheral ID 0-7 and Component ID 0-3 registers
    </p>
    <ul>
     <li>
      <p>
       If the value of the CMOD fields of both components equals zero, the components are identical
      </p>
     </li>
     <li>
      <p>
       If the CMOD fields of both components have the same non-zero value, it does not necessarily mean that they have been subjected to the same modifications.
      </p>
     </li>
     <li>
      <p>
       If the value of the CMOD field of either of the two components is non-zero, they might not be identical, even though they have the same values of the Peripheral ID 0-7 and Component ID 0-3 registers
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span id="mhur_mbx_mbx_pidr3__bits-3-0-reset-13">
     0x0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d7324e290" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7324e293" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7324e296" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d7324e299" rowspan="1">
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
    0x0FEC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_PIDR3
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
