# PFFCW<n>_PAY32, Postbox FIFO Channel Window <n> Payload Register (32bit access), n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--PAY32--Postbox-FIFO-Channel-Window--n--Payload-Register--32bit-access---n---0---63>

### PFFCW<n>\_PAY32, Postbox FIFO Channel Window <n> Payload Register (32bit access), n = 0 - 63

A 32bit access to the PFFCW<n>\_PAY register. The bit descriptions for this register depend on whether the access is a write or a read.

An access must be aligned to any 32bit boundary within the PFFCW\_PAY register, otherwise it is an unsupported access. It is implementation-defined whether the access is treated as RAZ/WI or modified to be an aligned access.

- 32bit accesses are only supported if PBX\_FFCH\_CFG0.P32BA\_SPT is set to 0b1.
- If PBX\_FFCH\_CFG0.P32BA\_SPT is set to 0b0, 32bit accesses are not supported. It is implementation-defined whether an unsupported access is treated as RAZ/WI or modified to a supported size.

The number of PFFCW<n>\_PAY32 registers depends on the PBX\_FFCH\_CFG0.P64BA\_SPT register field.

- If P64BA\_SPT is set to 1, there are two PFFCW<n>\_PAY32 registers, which occupy offsets 0x00-0x07 in the Postbox FIFO Channel Window <n>.
- If P64BA\_SPT is set to 0, the PFFCW<n>\_PAY32 register occupies offsets 0x00-0x04 and offsets 0x05 - 0x7 are reserved, within the Postbox FIFO Channel Window <n>.

A write access pushes the four bytes that are written to this offset onto the FIFO, if the FIFO has at least four byte of free space.

Read accesses return the number of bytes free space in the FIFO and whether the previous push operation generated an error or not.

### Configurations

This register is present only when FE is implemented and 32bit accesses are supported. Otherwise, direct accesses to PFFCW<n>\_PAY32 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offsets (4)
:   (64 \* n) + 0x2000,(64 \* n) + 0x2004

### Bit descriptions

When the access is a 32bit write that is aligned to an 32bit boundary, and the MHU implements 32bit accesses to the PFFCW<n>\_PAY register, the register has the following bit assignments.

Figure 1. PFFCW<n>\_PAY32\_PFFCW<n>\_PAY32 write bit assignments

![pffcw_n__pay32_pffcw_n__pay32 bit assignments](images/0131-PFFCW-n-_PAY32-Postbox-FIFO-Channel-Window-n-Payload-Register-32bit-access-n-0-63-img01.svg)

<table id="pffcw_n__pay32_pffcw_n__pay32__apffcwn_pay32-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFFCW&lt;n&gt;_PAY32 write bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d17506e185" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d17506e188" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d17506e191" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d17506e194" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [31:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PAY
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Payload to push onto FIFO
    </p>
    <p>
     Causes the written bytes of data to be pushed onto the FIFO, if there is at least four bytes of free space in the FIFO and sets the PFFCW&lt;n&gt;_ST.PPE field to be set to
     <span class="documents-g.number.bin">
      0b0
     </span>
     .
    </p>
    <p>
     If there is less than four bytes of free space in the FIFO, then no bytes are pushed onto the FIFO and the PFFCW&lt;n&gt;_ST.PPE field is set to
     <span class="documents-g.number.bin">
      0b1
     </span>
    </p>
    <p>
     The value written to this field has no effect on the operation of the FIFO.
    </p>
    <p>
     The order in which bytes are pushed onto the FIFO depends on the value of the PFFCW&lt;n&gt;_CTRL.MSBF field as follows:
    </p>
    <ul>
     <li>
      <p>
       <span class="documents-g.number.bin">
        0b0
       </span>
       - Bytes are pushed onto the FIFO starting with the LSB
      </p>
     </li>
     <li>
      <p>
       <span class="documents-g.number.bin">
        0b1
       </span>
       - Bytes are pushed onto the FIFO starting with the MSB
      </p>
     </li>
    </ul>
    <p>
     The MHU is a little endian device and considers the LSB to be the byte which is written to the lowest offsets accessed by the write.
    </p>
    <p>
     SOT flag is always associated with the first byte pushed onto the FIFO and EOT and ACK flags are associated with the last byte pushed onto the FIFO
    </p>
    <p>
     If the Transfer Delineation Mode for the FIFO is set to Partial or Auto Flag then on a write which sets PFFCW&lt;n&gt;_ST.PPE field to
     <span class="documents-g.number.bin">
      0b0
     </span>
     , the values of data flags in the PFFCW&lt;n&gt;_FLG register are updated.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="pffcw_n__pay32_pffcw_n__pay32__bits-31-0-reset-10">
     32{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

When the access is a 32bit read that is aligned to an 32bit boundary, and the MHU implements 32bit accesses to the PFFCW<n>\_PAY register, the register has the following bit assignments.

Figure 2. PFFCW<n>\_PAY32\_PFFCW<n>\_PAY32 read bit assignments

![pffcw_n__pay32_pffcw_n__pay32 bit assignments](images/0131-PFFCW-n-_PAY32-Postbox-FIFO-Channel-Window-n-Payload-Register-32bit-access-n-0-63-img02.svg)

<table id="pffcw_n__pay32_pffcw_n__pay32__apffcwn_pay32-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   PFFCW&lt;n&gt;_PAY32 read bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d17506e308" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d17506e311" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d17506e314" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d17506e317" rowspan="1">
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
    PPE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Previous Push Error
    </p>
    <p>
     Indicates whether a previous push to the FIFO caused an error
    </p>
    <p>
     An error occurs due to the FIFO not having enough space to push all the bytes provided in the last write to the PFFCW_PAY register.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error has occurred on the last push operation
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An error has occurred on the last push operation
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <code>
     -
    </code>
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
    FFS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     FIFO Free Space
    </p>
    <p>
     Indicates the number of invalid bytes in the FIFO
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000000
      </span>
     </dt>
     <dd>
      <p>
       No free bytes in the FIFO
      </p>
     </dd>
    </dl>
    <p>
     The maximum value returned is never greater than the FIFO Depth
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The reset value for this field depends on the MHU configuration.
    </p>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
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
   <th class="documents-nocellnorowborder" colspan="1" id="d17506e444" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d17506e447" rowspan="1">
    Offset
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d17506e450" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PFFCW&lt;n&gt;_PAY32
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [(64 * n) + 0x2000]
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    63:0
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PFFCW&lt;n&gt;_PAY32
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [(64 * n) + 0x2004]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    63:0
   </td>
  </tr>
 </tbody>
</table>
