# MBX_FCFG_ERRINS, Mailbox FIFO channel config RAM ECC Error Insertion Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MBX-FCFG-ERRINS--Mailbox-FIFO-channel-config-RAM-ECC-Error-Insertion-Register>

### MBX\_FCFG\_ERRINS, Mailbox FIFO channel config RAM ECC Error Insertion Register

Enables ECC error insertion in the Mailbox FIFO channel configuration RAM. The bit descriptions for this register depend on whether the access is a write or a read.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   MHUR.MBX

Register offset
:   0xF020

### Bit descriptions

When the access is a write, the MBX\_FCFG\_ERRINS register has the following bit assignments.

Figure 1. MHUR.MBX\_MBX\_FCFG\_ERRINS write bit assignments

![mhur.mbx_mbx_fcfg_errins bit assignments](images/0245-MBX_FCFG_ERRINS-Mailbox-FIFO-channel-config-RAM-ECC-Error-Insertion-Register-img01.svg)

<table id="mhur_mbx_mbx_fcfg_errins__ambx_fcfg_errins-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MBX_FCFG_ERRINS write bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d132482e163" rowspan="1">
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
    <span id="mhur_mbx_mbx_fcfg_errins__bits-63-reset-6">
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
    <span id="mhur_mbx_mbx_fcfg_errins__bits-60-reset-6">
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
    <code id="mhur_mbx_mbx_fcfg_errins__bits-47-32-reset-6">
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
    <span id="mhur_mbx_mbx_fcfg_errins__bits-31-reset-9">
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
    <code id="mhur_mbx_mbx_fcfg_errins__bits-24-16-reset-3">
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
    <span id="mhur_mbx_mbx_fcfg_errins__bits-15-reset-3">
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
    <code id="mhur_mbx_mbx_fcfg_errins__bits-8-0-reset-6">
     9{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

When the access is a read, the MBX\_FCFG\_ERRINS register has the following bit assignments.

Figure 2. MHUR.MBX\_MBX\_FCFG\_ERRINS read bit assignments

![mhur.mbx_mbx_fcfg_errins bit assignments](images/0245-MBX_FCFG_ERRINS-Mailbox-FIFO-channel-config-RAM-ECC-Error-Insertion-Register-img02.svg)

<table id="mhur_mbx_mbx_fcfg_errins__ambx_fcfg_errins-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   MBX_FCFG_ERRINS read bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e441" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e444" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e447" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d132482e450" rowspan="1">
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
    <span id="mhur_mbx_mbx_fcfg_errins__bits-62-61-reset-7">
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
    <span id="mhur_mbx_mbx_fcfg_errins__bits-60-reset-7">
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
    <code id="mhur_mbx_mbx_fcfg_errins__bits-47-32-reset-7">
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
    <code id="mhur_mbx_mbx_fcfg_errins__bits-8-0-reset-7">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e730" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e733" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d132482e736" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d132482e739" rowspan="1">
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
    0xF020
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MBX_FCFG_ERRINS
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
