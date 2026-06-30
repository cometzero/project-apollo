# MFFCW<n>_FLG64, Mailbox FIFO Channel Window <n> Flag Register (64bit access), n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--FLG64--Mailbox-FIFO-Channel-Window--n--Flag-Register--64bit-access---n---0---63>

### MFFCW<n>\_FLG64, Mailbox FIFO Channel Window <n> Flag Register (64bit access), n = 0 - 63

A 64bit access to the MFFCW<n>\_FLG register.

An access must be aligned to any 64bit boundary in the MFFCW<n>\_FLG register, otherwise the access is treated as RAZ/WI.

- 64bit accesses are only supported if MBX\_FFCH\_CFG0.M64BA\_SPT is set to 0b1.
- If MBX\_FFCH\_CFG0.M64BA\_SPT is set to 0b1, 64bit accesses are not supported. It is implementation-defined whether an unsupported access is treated as RAZ/WI or modified to a supported size.

The MFFCW<n>\_FLG register occupies offsets 0x08-0x0F in the Mailbox FIFO Channel Window <n>.

A read of this register returns:

- The contents of the Flag History Buffer
- Current fill level of the FIFO

This register is expected to be read after a read of the MFFCW<n>\_PAY register to get the data flags associated with the bytes read from the FIFO. The read of this register must be of the same size as the read of the MFFCW<n>\_PAY register, otherwise it can lead to loss or corruption of information.

### Configurations

This register is present only when FE is implemented and 64 bit access are supported. Otherwise, direct accesses to MFFCW<n>\_FLG64 are RAZ/WI.

### Attributes

Width
:   64

Component
:   MHUR.MBX

Register offset
:   (64 \* n) + 0x2008

### Bit descriptions

Figure 1. MFFCW<n>\_FLG64\_MFFCW<n>\_FLG64 bit assignments

![mffcw_n__flg64_mffcw_n__flg64 bit assignments](images/0231-MFFCW-n-_FLG64-Mailbox-FIFO-Channel-Window-n-Flag-Register-64bit-access-n-0-63-img01.svg)

<table id="mffcw_n__flg64_mffcw_n__flg64__amffcwn_flg64-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MFFCW&lt;n&gt;_FLG64 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d21868e203" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21868e206" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21868e209" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d21868e212" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:53]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FFL
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     FIFO Fill Level
    </p>
    <p>
     Indicates the number of bytes containing valid data in the FIFO
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000000
      </span>
     </dt>
     <dd>
      <p>
       All bytes in the FIFO are invalid
      </p>
     </dd>
    </dl>
    <p>
     The maximum value returned is never greater than the FIFO Depth
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <code id="mffcw_n__flg64_mffcw_n__flg64__bits-63-53-reset">
     11{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [52:31, 27, 23, 19, 15, 11, 7, 3]
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
    [30, 26, 22, 18, 14, 10, 6, 2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    VFLG&lt;m&gt;
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Valid Flag &lt;m&gt;
    </p>
    <p>
     Indicates whether FLG&lt;m&gt; field contains valid data or not.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       FLG&lt;m&gt; is not valid
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FLG&lt;m&gt; is valid
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [29:28, 25:24, 21:20, 17:16, 13:12, 9:8, 5:4, 1:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    FLG&lt;m&gt;
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Flag &lt;m&gt;
    </p>
    <p>
     Provides the data flags, except for the ACK flag, held in FHB entry 0 to 7 and whether the data flags are valid or invalid.
    </p>
    <p>
     The association of the FLG&lt;m&gt; field to the FHB entries depends on the value of the MFFCW&lt;n&gt;_CTRL.MSBF field when the read of the MFFCW&lt;n&gt;_FLG register occurs
    </p>
    <p>
     MFFCW&lt;n&gt;_CTRL.MSBF ==
     <span class="documents-g.number.bin">
      0b0
     </span>
    </p>
    <p>
     FLG0 is associated with FHB entry 0 and FLG7 is associated with FHB entry 7
    </p>
    <p>
     MFFCW&lt;n&gt;_CTRL.MSBF ==
     <span class="documents-g.number.bin">
      0b1
     </span>
    </p>
    <p>
     FLG0 is associated with FHB entry 7 and FLG7 is associated with FHB entry 0
    </p>
    <p>
     The legal values of the FLG&lt;m&gt; field, when VFLG&lt;m&gt; is set to
     <span class="documents-g.number.bin">
      0b1
     </span>
     are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Payload
      </p>
      <p>
       Neither the first or last byte of a Transfer
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Start Byte
      </p>
      <p>
       First byte of a Transfer
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       End Byte
      </p>
      <p>
       Last byte of a Transfer
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Start and End Byte
      </p>
      <p>
       First and last byte of a Transfer
      </p>
     </dd>
    </dl>
    <p>
     The value of the FLG&lt;m&gt; field is only valid if VFLG&lt;m&gt; is set to
     <span class="documents-g.number.bin">
      0b1
     </span>
     , otherwise the value of this field must be ignored by software.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mffcw_n__flg64_mffcw_n__flg64__bits-29-28--25-24--21-20--17-16--13-12--9-8--5-4--1-0-reset">
     16{x}
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
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d21868e430" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d21868e433" rowspan="1">
    Offset
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d21868e436" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MFFCW&lt;n&gt;_FLG64
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [(64 * n) + 0x2008]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    63:0
   </td>
  </tr>
 </tbody>
</table>
