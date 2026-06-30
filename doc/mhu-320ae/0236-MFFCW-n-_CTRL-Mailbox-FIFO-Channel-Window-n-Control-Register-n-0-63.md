# MFFCW<n>_CTRL, Mailbox FIFO Channel Window <n> Control Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--CTRL--Mailbox-FIFO-Channel-Window--n--Control-Register--n---0---63>

### MFFCW<n>\_CTRL, Mailbox FIFO Channel Window <n> Control Register, n = 0 - 63

This register contains control bits for FIFO channels

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to MFFCW<n>\_CTRL are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   (64 \* n) + 0x2020

### Bit descriptions

Figure 1. MHUR.MBX\_MFFCW<n>\_CTRL bit assignments

![mhur.mbx_mffcw_n__ctrl bit assignments](images/0236-MFFCW-n-_CTRL-Mailbox-FIFO-Channel-Window-n-Control-Register-n-0-63-img01.svg)

<table id="mhur_mbx_mffcw_n__ctrl__amffcwn_ctrl-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MFFCW&lt;n&gt;_CTRL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d93359e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d93359e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d93359e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d93359e163" rowspan="1">
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
     FIFO Flush
    </p>
    <p>
     Request a flush of the FFCH
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No request to flush the FIFO
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Request to flush the FIFO
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
    [30:4]
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
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FTAB
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Future Transfer Auto Buffering
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Future Transfer Auto Buffering is not enabled
      </p>
      <p>
       The value of flags associated with bytes read from the FIFO have no effect on the number of bytes read from the FIFO
      </p>
      <p>
       A request to pop bytes from the FIFO is not affected
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Future Transfer Auto Buffering is enabled
      </p>
      <p>
       When a read of the MFFCW&lt;n&gt;_PAY registers with an access size greater than 1 occurs, any bytes read from the FIFO after the first byte with the EOT field set to 0b1 has been detected, are:
      </p>
      <ul>
       <li>
        <p>
         Not read or popped from the FIFO
        </p>
       </li>
       <li>
        <p>
         the bytes are set to an
         <span class="documents-archterm">
          UNKNOWN
         </span>
         value in the read data response
        </p>
       </li>
       <li>
        <p>
         entries in the Flag History Buffer are set to invalid
        </p>
       </li>
      </ul>
      <p>
       Only bytes up to the first byte read from the FIFO with the EOT field set to 0b1 are popped from the FIFO
      </p>
     </dd>
    </dl>
    <p>
     Must be used with the RA_EN field set to
     <span class="documents-g.number.bin">
      0b1
     </span>
     , otherwise the field is considered to be
     <span class="documents-g.number.bin">
      0b0
     </span>
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
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RA_EN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Controls whether Read to acknowledge is enabled
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Read acknowledge is not enabled
      </p>
      <p>
       Bytes are popped from the FIFO by writing to MFFCW&lt;n&gt;_PAY register.
      </p>
      <p>
       The number of bytes popped from the FIFO is determined by the:
      </p>
      <ul>
       <li>
        <p>
         Size of the access to the MFFCW&lt;n&gt;_PAY
        </p>
       </li>
       <li>
        <p>
         Lowest offset within the MFFCW&lt;n&gt;_PAY register the access targets.
        </p>
       </li>
       <li>
        <p>
         Number of valid bytes in the FIFO
        </p>
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
       Read acknowledge is enabled
      </p>
      <p>
       Bytes are popped from the FIFO by reading the MFFCW&lt;n&gt;_PAY register.
      </p>
      <p>
       The number of bytes popped from the FIFO is determined by the:
      </p>
      <ul>
       <li>
        <p>
         Size of the access
        </p>
       </li>
       <li>
        <p>
         FTAB field value
        </p>
       </li>
       <li>
        <p>
         Value of the EOT flag for a byte which is popped from the FIFO due to this read, when the FTAB field is set 0b1
        </p>
       </li>
       <li>
        <p>
         Lowest offset within the MFFCW&lt;n&gt;_PAY that is targeted by the read access
        </p>
       </li>
       <li>
        <p>
         Number of valid bytes in the FIFO
        </p>
       </li>
      </ul>
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
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MSBF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Most Significant Byte First
    </p>
    <p>
     Selects the order in which bytes are pushed onto the FIFO when multiple bytes are to be pushed due to a single write to the MFFCW&lt;n&gt;_PAY register
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Least Significant Byte first
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Most Significant Byte first
      </p>
     </dd>
    </dl>
    <p>
     FFCH are considered little endian and the LSB is the byte lowest offset within the access and the MSB is the highest byte offset within the access
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
    MBX_COMB_EN
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       FIFO Channel does not contribute to the Mailbox Combined interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FIFO Channel contributes to the Mailbox Combined interrupt
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
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
   <th class="documents-nocellnorowborder" colspan="1" id="d93359e558" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d93359e561" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d93359e564" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d93359e567" rowspan="1">
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
    (64 * n) + 0x2020
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MFFCW&lt;n&gt;_CTRL
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
