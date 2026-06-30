# Register map pages

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/Register-map-pages>

### Register map pages

The MHU-320AE MHU Sender and MHU Receiver address maps contain multiple pages. The number of pages and address aliasing depends on the MHU-320AE configuration.

The MHU-320AE registers are grouped into 64KB blocks, each of which is formed of multiple 4KB pages.

MHU-320AE always retains the following block order:

1. MHU Sender or MHU Receiver Security Control block, if `SENDER/REG_SECURITY_TYPE != none` or `RECEIVER/REG_SECURITY_TYPE != none` respectively
2. Postbox or Mailbox block
3. MHU Sender or MHU Receiver RAS block

For example if the MHU-320AE configuration has MHU Sender Security Control and MHU Receiver Security Control register blocks present in the configuration, the following block offsets are used for the register blocks (same as the programmers model presented in this document):

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MHU blocks with security blocks present
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d3476e127" rowspan="1">
    <p>
     Block offset
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d3476e131" rowspan="1">
    <p>
     Block
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     MHU Sender or MHU Receiver Security Control
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x10000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Postbox or Mailbox
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x20000
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     MHU Sender or MHU Receiver RAS
    </p>
   </td>
  </tr>
 </tbody>
</table>

Alternatively, the following block offsets are used if both security blocks are not present in the configuration:

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   MHU blocks without security blocks present
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d3476e197" rowspan="1">
    <p>
     Block offset
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d3476e201" rowspan="1">
    <p>
     Block
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Postbox or Mailbox
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x10000
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     MHU Sender or MHU Receiver RAS
    </p>
   </td>
  </tr>
 </tbody>
</table>
