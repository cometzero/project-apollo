# PBX_FIFO_ERRINS, Postbox FIFO channel RAM ECC Error Insertion Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FIFO-ERRINS--Postbox-FIFO-channel-RAM-ECC-Error-Insertion-Register>

### PBX\_FIFO\_ERRINS, Postbox FIFO channel RAM ECC Error Insertion Register

Enables ECC error insertion in the Postbox FIFO channel RAM. The bit descriptions for this register depend on whether the access is a read or a write.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   MHUS.PBX

Register offset
:   0xF010

### Bit descriptions

When the access is a write, the PBX\_FIFO\_ERRINS register has the following bit assignments.

Figure 1. MHUS.PBX\_PBX\_FIFO\_ERRINS write bit assignments

![mhus.pbx_pbx_fifo_errins bit assignments](images/0143-PBX_FIFO_ERRINS-Postbox-FIFO-channel-RAM-ECC-Error-Insertion-Register-img01.svg)

<table id="mhus_pbx_pbx_fifo_errins__apbx_fifo_errins-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PBX_FIFO_ERRINS write bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d111212e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    VALID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Writing 1'b1 triggers starting error insertion operation.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span id="mhus_pbx_pbx_fifo_errins__bits-63-reset-1">
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [62:61]
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
    [60]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DWC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Disable Write Check. If set, tests the ECC encoder.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span id="mhus_pbx_pbx_fifo_errins__bits-60-reset">
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [59:48]
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
    [47:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ADDR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RAM address that required error will be inserted at.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <code id="mhus_pbx_pbx_fifo_errins__bits-47-32-reset">
     16{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ERRINS2VALID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     If set, enables insertion of second RAM error in bit location specified by ERRINS2LOC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span id="mhus_pbx_pbx_fifo_errins__bits-31-reset-6">
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30:25]
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
    [24:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ERRINS2LOC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Defines bit location for second inserted RAM error
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <code id="mhus_pbx_pbx_fifo_errins__bits-24-16-reset">
     9{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ERRINS1VALID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     If set, enables insertion of first RAM error in bit location specified by ERRINS1LOC
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span id="mhus_pbx_pbx_fifo_errins__bits-15-reset">
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [14:9]
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
    [8:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERRINS1LOC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Defines bit location for first inserted RAM error
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mhus_pbx_pbx_fifo_errins__bits-8-0-reset">
     9{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

When the access is a read, the PBX\_FIFO\_ERRINS register has the following bit assignments.

Figure 2. MHUS.PBX\_PBX\_FIFO\_ERRINS read bit assignments

![mhus.pbx_pbx_fifo_errins bit assignments](images/0143-PBX_FIFO_ERRINS-Postbox-FIFO-channel-RAM-ECC-Error-Insertion-Register-img02.svg)

<table id="mhus_pbx_pbx_fifo_errins__apbx_fifo_errins-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   PBX_FIFO_ERRINS read bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e441" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e444" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e447" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d111212e450" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    VALID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if error insertion operation is ongoing
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error insertion operation is in progress.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Error insertion operation is in progress.
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
    [62:61]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    STATUS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Result of error insertion when VALID is read as 1'b0
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Error insertion was successful.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Error insertion encountered out of range address or bit location.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Error insertion overlap with real ECC error.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Encoder/decoder mismatch during error insertion.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span id="mhus_pbx_pbx_fifo_errins__bits-62-61-reset-1">
     xx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [60]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PRESENT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     If set, indicates that RAM is present and allows inserting errors
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span id="mhus_pbx_pbx_fifo_errins__bits-60-reset-1">
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [59:48]
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
    [47:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DEPTH
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Defines the maximum RAM address for insertion
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <code id="mhus_pbx_pbx_fifo_errins__bits-47-32-reset-1">
     16{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:9]
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
    [8:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    WIDTH
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Defines the maximum RAM bit location for insertion
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mhus_pbx_pbx_fifo_errins__bits-8-0-reset-1">
     9{x}
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
    Table 3.
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
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e730" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e733" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d111212e736" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d111212e739" rowspan="1">
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
    0xF010
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PBX_FIFO_ERRINS
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
