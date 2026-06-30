# MFFCW<n>_ST, Mailbox FIFO Channel Window <n> Status Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--ST--Mailbox-FIFO-Channel-Window--n--Status-Register--n---0---63>

### MFFCW<n>\_ST, Mailbox FIFO Channel Window <n> Status Register, n = 0 - 63

Contains status information for FIFO channel

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to MFFCW<n>\_ST are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   (64 \* n) + 0x2024

### Bit descriptions

Figure 1. MHUR.MBX\_MFFCW<n>\_ST bit assignments

![mhur.mbx_mffcw_n__st bit assignments](images/0237-MFFCW-n-_ST-Mailbox-FIFO-Channel-Window-n-Status-Register-n-0-63-img01.svg)

<table id="mhur_mbx_mffcw_n__st__amffcwn_st-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MFFCW&lt;n&gt;_ST bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d2636e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d2636e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d2636e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d2636e163" rowspan="1">
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
     FIFO Flush.
    </p>
    <p>
     Status of a flush of the FFCH.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The meaning of this value depends on the value of the FF field in the corresponding MFFCW&lt;n&gt;_CTRL register:
      </p>
      <ul id="mhur_mbx_mffcw_n__st__ul_ims_rl1_tzb">
       <li>
        When MFFCW_CTRL&lt;n&gt;.FF is 0b0 - Receiver FIFO flush mechanism is idle
       </li>
      </ul>
      <ul id="mhur_mbx_mffcw_n__st__ul_rbr_tl1_tzb">
       <li>
        When MFFCW_CTRL&lt;n&gt;.FF is 0b1 - Receiver FIFO flush mechanism is performing a flush
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
       FIFO flush complete
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
    [30:11]
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
    FFL
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     FIFO Fill Level.
    </p>
    <p>
     Indicates the number of bytes containing valid data in the FIFO.
    </p>
    <p>
     The maximum value returned is never greater than the FIFO Depth.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mhur_mbx_mffcw_n__st__bits-10-0-reset">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d2636e295" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d2636e298" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d2636e301" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d2636e304" rowspan="1">
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
    (64 * n) + 0x2024
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MFFCW&lt;n&gt;_ST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
