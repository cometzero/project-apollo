# MFFCW<n>_FIFO_POP, Mailbox FIFO Channel Window <n> FIFO POP Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FIFO-POP--Mailbox-FIFO-Channel-Window--n--FIFO-POP-Register--n---0---63>

### MFFCW<n>\_FIFO\_POP, Mailbox FIFO Channel Window <n> FIFO POP Register, n = 0 - 63

Register for popping bytes from a FIFO channel when writing to it

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to MFFCW<n>\_FIFO\_POP are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   (64 \* n) + 0x2028

### Bit descriptions

Figure 1. MHUR.MBX\_MFFCW<n>\_FIFO\_POP bit assignments

![mhur.mbx_mffcw_n__fifo_pop bit assignments](images/0238-MFFCW-n-_FIFO_POP-Mailbox-FIFO-Channel-Window-n-FIFO-POP-Register-n-0-63-img01.svg)

<table id="mhur_mbx_mffcw_n__fifo_pop__amffcwn_fifo_pop-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MFFCW&lt;n&gt;_FIFO_POP bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d16262e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16262e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16262e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d16262e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:3]
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
    [2:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    POP
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of bytes to pop from the FIFO. This is the maximum number of bytes popped from the FIFO. The number of bytes actually popped from the FIFO is as follows:
    </p>
    <ul>
     <li>
      <p>
       When MFFCW&lt;n&gt;_CTRL.RA_EN is set to
       <span class="documents-g.number.bin">
        0b1
       </span>
       no bytes are popped from the FIFO.
      </p>
     </li>
     <li>
      <p>
       When MFFCW&lt;n&gt;_CTRL.RA_EN is set to
       <span class="documents-g.number.bin">
        0b0
       </span>
       the number of bytes is the smallest of the following:
      </p>
      <ul>
       <li>
        <p>
         Value written to this field.
        </p>
       </li>
       <li>
        <p>
         Number of valid bytes in the FIFO.
        </p>
       </li>
      </ul>
     </li>
    </ul>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       It is IMPDEF whether:
      </p>
      <ul>
       <li>
        <p>
         No bytes are popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         The value is treated as another supported value
        </p>
       </li>
      </ul>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       It is IMPDEF whether:
      </p>
      <ul>
       <li>
        <p>
         No bytes are popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         The value is treated as another supported value
        </p>
       </li>
      </ul>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       It is IMPDEF whether:
      </p>
      <ul>
       <li>
        <p>
         No bytes are popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         The value is treated as another supported value
        </p>
       </li>
      </ul>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b011
      </span>
     </dt>
     <dd>
      <p>
       When M32BA_SPT, maximum of 4 bytes are popped from the FIFO.
      </p>
      <p>
       When !M32BA_SPT, it is IMPDEF whether:
      </p>
      <ul>
       <li>
        <p>
         No bytes are popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         The value is treated as another supported value
        </p>
       </li>
      </ul>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b100
      </span>
     </dt>
     <dd>
      <p>
       It is IMPDEF whether:
      </p>
      <ul>
       <li>
        <p>
         No bytes are popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         The value is treated as another supported value
        </p>
       </li>
      </ul>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b101
      </span>
     </dt>
     <dd>
      <p>
       It is IMPDEF whether:
      </p>
      <ul>
       <li>
        <p>
         No bytes are popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         The value is treated as another supported value
        </p>
       </li>
      </ul>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b110
      </span>
     </dt>
     <dd>
      <p>
       It is IMPDEF whether:
      </p>
      <ul>
       <li>
        <p>
         No bytes are popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         The value is treated as another supported value
        </p>
       </li>
      </ul>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b111
      </span>
     </dt>
     <dd>
      <p>
       When !M64BA_SPT, it is IMPDEF whether:
      </p>
      <ul>
       <li>
        <p>
         No bytes are popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         The value is treated as another supported value
        </p>
       </li>
      </ul>
      <p>
       When M64BA_SPT, maximum of 8 bytes are popped from the FIFO.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
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
   <th class="documents-nocellnorowborder" colspan="1" id="d16262e457" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16262e460" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16262e463" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d16262e466" rowspan="1">
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
    (64 * n) + 0x2028
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MFFCW&lt;n&gt;_FIFO_POP
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
