# PFFCW<n>_ST, Postbox FIFO Channel Window <n> Status Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ST--Postbox-FIFO-Channel-Window--n--Status-Register--n---0---63>

### PFFCW<n>\_ST, Postbox FIFO Channel Window <n> Status Register, n = 0 - 63

Contains status information for FIFO channel

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to PFFCW<n>\_ST are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (64 \* n) + 0x2024

### Bit descriptions

Figure 1. MHUS.PBX\_PFFCW<n>\_ST bit assignments

![mhus.pbx_pffcw_n__st bit assignments](images/0137-PFFCW-n-_ST-Postbox-FIFO-Channel-Window-n-Status-Register-n-0-63-img01.svg)

<table id="mhus_pbx_pffcw_n__st__apffcwn_st-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFFCW&lt;n&gt;_ST bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d135202e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d135202e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d135202e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d135202e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Status of Sender FIFO flush mechanism.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The meaning of this value depends on the value of the FF field in the corresponding PFFCW&lt;n&gt;_CTRL register.
      </p>
      <ul>
       <li>
        When PFFCW_CTRL&lt;n&gt;.FF is 0b0, the Sender FIFO flush mechanism is idle.
       </li>
       <li>
        When PFFCW_CTRL&lt;n&gt;.FF is 0b1, the Sender FIFO flush mechanism is performing a flush.
       </li>
      </ul>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Sender FIFO flush completed.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30:17]
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
    [16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PPE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Previous Push Error.
    </p>
    <p>
     Indicates whether a previous push to the FIFO caused an error.
    </p>
    <p>
     An error is when the previous push operation did not push all the bytes requested onto the FIFO.
    </p>
    <p>
     The reason for why bytes could not be pushed onto the FIFO are:
    </p>
    <ul>
     <li>
      <p>
       Not enough space in the FIFO
      </p>
     </li>
     <li>
      <p>
       The write to the PPFCW_PAY register did not meet the access conditions for the PFFCW&lt;n&gt;_PAY register for this implementation of the MHU.
      </p>
     </li>
    </ul>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error has occurred on the last push operation.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An error has occurred on the last push operation.
      </p>
     </dd>
    </dl>
    <p>
     If there has been no previous push operation to the FIFO this field is
     <span class="documents-g.number.bin">
      0b0
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:11]
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
    [10:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FFS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     FIFO Free Space.
    </p>
    <p>
     Indicates the number of invalid bytes in the FIFO. The maximum value returned is never greater than the FIFO Depth.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mhus_pbx_pffcw_n__st__bits-10-0-reset-2">
     11{x}
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
   <th class="documents-nocellnorowborder" colspan="1" id="d135202e369" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d135202e372" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d135202e375" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d135202e378" rowspan="1">
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
    (64 * n) + 0x2024
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PFFCW&lt;n&gt;_ST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
