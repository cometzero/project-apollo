# MFFCW<n>_PAY64, Mailbox FIFO Channel Window <n> Payload Register (64bit access), n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--PAY64--Mailbox-FIFO-Channel-Window--n--Payload-Register--64bit-access---n---0---63>

### MFFCW<n>\_PAY64, Mailbox FIFO Channel Window <n> Payload Register (64bit access), n = 0 - 63

A 64bit access to the MFFCW<n>\_PAY register.

An access must be aligned to any 8bit boundary in the MFFCW<n>\_PAY register, otherwise it is an unsupported access. It I is implementation-defined whether the access is treated as RAZ/WI or modified to be an aligned access.

- 64bit accesses are only supported, if MBX\_FFCH\_CFG0.M64BA\_SPT is set to 0b1.
- If MBX\_FFCH\_CFG0.M64BA\_SPT is set to 0b0, 64bit accesses are not supported. It is implementation-defined whether unsupported accesses are treated as RAZ/WI or modified to a supported size.

MFFCW<n>\_PAY register occupies offsets 0x00-0x07 in the Mailbox FIFO Channel Window <n>.

A read of this register reads up to eight bytes starting at the head of the FIFO, if the FIFO is not empty otherwise an IMPDEF value is returned.

If the MFFCW<n>\_CTRL.RA\_EN field is set to 0b1, the bytes read from the FIFO is also popped from the FIFO.

On a read of this register, the values of the data flags, associated with the bytes read from the FIFO are stored in the Flag History Buffer.

### Configurations

This register is present only when FE is implemented and M64BA\_SPT. Otherwise, direct accesses to MFFCW<n>\_PAY64 are RAZ/WI.

### Attributes

Width
:   64

Component
:   MHUR.MBX

Register offset
:   (64 \* n) + 0x2000

### Bit descriptions

A 64bit read access, aligned to a 64bit boundary, when the MHU implements 64bit accesses to the register

Figure 1. MFFCW<n>\_PAY64\_MFFCW<n>\_PAY64 bit assignments

![mffcw_n__pay64_mffcw_n__pay64 bit assignments](images/0229-MFFCW-n-_PAY64-Mailbox-FIFO-Channel-Window-n-Payload-Register-64bit-access-n-0-63-img01.svg)

<table id="mffcw_n__pay64_mffcw_n__pay64__amffcwn_pay64-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MFFCW&lt;n&gt;_PAY64 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d71597e188" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d71597e191" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d71597e194" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d71597e197" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [63:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PAY
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Payload read from FIFO.
    </p>
    <p>
     Eight bytes are read from the FIFO, starting from the head of the FIFO.
    </p>
    <p>
     A byte read from the FIFO can be either valid or invalid. A valid byte has an 8bit data value and data flags associated with it. An invalid byte has an IMPDEF data value and no data flags associated with it.
    </p>
    <p>
     The data values of all bytes read from the FIFO, are arrange in the PAY field depending on the value of the MFFCW&lt;n&gt;_CTRL.MSBF field and the byte number.
    </p>
    <p>
     MFFCW&lt;n&gt;_CTRL.MSBF ==
     <span class="documents-g.number.bin">
      0b0
     </span>
    </p>
    <p>
     Bytes are arranged in ascending order starting with the first byte read from the FIFO in the LSB of the PAY field and the last byte read from the FIFO in the MSB of the PAY field.
    </p>
    <p>
     MFFCW&lt;n&gt;_CTRL.MSBF ==
     <span class="documents-g.number.bin">
      0b1
     </span>
    </p>
    <p>
     Bytes are arranged in ascending order starting with the first byte read from the FIFO in the MSB of the PAY field and the last byte read from the FIFO in the LSB of the PAY field.
    </p>
    <p>
     The data flags of each byte are stored in the Flag History Buffer(FHB) starting with the first byte read in the entry 0 of the FHB, with all other entries being marked as invalid.
    </p>
    <p>
     If MFFCW&lt;n&gt;_CTRL.RA_EN is set to
     <span class="documents-g.number.bin">
      0b1
     </span>
     , when a byte is read from the FIFO:
    </p>
    <ul>
     <li>
      <p>
       IT is also removed from the FIFO.
      </p>
     </li>
     <li>
      <p>
       A Transfer Acknowledge event is generated if that byte was associated with the ACK and EOT data flags.
      </p>
     </li>
    </ul>
    <p>
     Otherwise the byte still remains in the FIFO and a subsequent read of the same size would return the same bytes.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     See description.
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
   <th class="documents-nocellnorowborder" colspan="1" id="d71597e303" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d71597e306" rowspan="1">
    Offset
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d71597e309" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MFFCW&lt;n&gt;_PAY64
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [(64 * n) + 0x2000]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    63:0
   </td>
  </tr>
 </tbody>
</table>
