# Bus errors

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Bus-errors>

### Bus errors

APB5 or ACE5-Lite bus error syndromes such as bad transactions, and corrupted RAM data reads can be made to report an APB5 or ACE-Lite external Subordinate response error (SLVERR).

The [SRAS\_ERR<n>CTLR](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary/SRAS-ERR-n-CTLR--Error-Record--n--Control-Register--n---0---3?lang=en "The error control register contains enable bits for the node that writes to this record.").UE and [RRAS\_ERR<n>CTLR](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-CTLR--Error-Record--n--Control-Register--n---0---9?lang=en "The error control register contains enable bits for the node that writes to this record.").UE register bits can be used to enable or disable this error in the MHU Sender or MHU Receiver for the syndromes shown in the following table.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Bus error syndromes
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d13618e118" rowspan="1">
    <p>
     Syndrome
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d13618e122" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d13618e126" rowspan="1">
    <p>
     Access
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SYN_REG_BAD
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Programming access is either illegal or unrecognized
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Read and write
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SYN_REC_DB_CORRUPTED
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Data read from doorbell channel RAM is corrupted.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Read
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SYN_REC_FST_CORRUPTED
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Data read from fast channel RAM is corrupted
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Read
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     SYN_FIFO_CORRUPTED
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Data read from FIFO channel RAM is corrupted
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Read
    </p>
   </td>
  </tr>
 </tbody>
</table>
