# MHU Sender and MHU Receiver software error records, Record 0

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-and-MHU-Receiver-software-error-records--Record-0>

### MHU Sender and MHU Receiver software error records, Record 0

Software error record 0 contains software errors that are uncorrectable both in the MHU Sender and MHU Receiver.

Record 0 contains software programming errors from a wide range of sources within the MHU-320AE. In general, these errors are contained. For uncorrected errors, the information that is provided gives enough information to enable recovery without significant loss of functionality.

We recommend that record 0 is connected to a high priority interrupt within the system. This connection prevents the record from overflowing if it receives more errors than it is able to process with the possible loss of information that is required for recovery.

The following table describes the syndromes that are recorded in record 0, the reported information, and recovery instructions.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Software errors, record 0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d100592e113" rowspan="1">
    <p>
     ERR&lt;n&gt;STATUS.IERR (Syndrome)
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d100592e117" rowspan="1">
    <p>
     ERR&lt;n&gt;STATUS.SERR
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d100592e121" rowspan="1">
    <p>
     ERR&lt;n&gt;MISC1 data description
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d100592e125" rowspan="1">
    <p>
     Recovery and prevention
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
     , SYN_REG_BAD Illegal subordinate access
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     AccessRnW, bit [11] AccessSize, bits [10:8] AccessLength, bits [7:0]
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Repeat illegal access, with appropriate size and properties. Full access address is given in ERR&lt;n&gt;ADDR.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1
     </span>
     , SYN_REC_DB_CORRUPTED Data read from doorbell channel that encountered an uncorrectable error
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x6
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     None
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Software has tried to read corrupted data that is stored in MHU Receiver doorbell channel RAM. Check the relevant RAM error record. Full access address is given in ERR&lt;n&gt;ADDR in MHU Receiver.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x2
     </span>
     , SYN_REC_FST_CORRUPTED Data read from fast channel that encountered an uncorrectable error
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x6
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     None
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Software has tried to read corrupted data that is stored in MHU Receiver fast channel RAM. Check the relevant RAM error record. Full access address is given in ERR&lt;n&gt;ADDR in MHU Receiver.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x3
     </span>
     , SYN_FIFO_CORRUPTED Data read from FIFO channel that encountered an uncorrectable error
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x6
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     None
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Software has tried to read corrupted data that is stored in MHU Sender or MHU Receiver FIFO channel RAM. Check the relevant RAM error record. Full access address is given in ERR&lt;n&gt;ADDR.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4
     </span>
     , SYN_ACE_CC_BAD Illegal ACE5-Lite subordinate access on communications interface
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     LenErr, bit [2] StrbErr, bit [1] LastErr, bit [0]
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The MHU communications interface received an ACE5-Lite access of an unexpected type, as indicated by the MISC1 information. The communications interface expects a single-beat, 64-bit access .
    </p>
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> You can use the SRAS\_ERR0CTLR.DAE and RRAS\_ERR0CTLR.DAE bits in the MHU Sender and MHU Receiver to disable error reporting for illegal subordinate accesses (SYN\_REG\_BAD syndrome). For more information, see either [SRAS\_ERR<n>CTLR](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary/SRAS-ERR-n-CTLR--Error-Record--n--Control-Register--n---0---3?lang=en "The error control register contains enable bits for the node that writes to this record.") or [RRAS\_ERR<n>CTLR](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-CTLR--Error-Record--n--Control-Register--n---0---9?lang=en "The error control register contains enable bits for the node that writes to this record.").
