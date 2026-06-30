# MHU Receiver FIFO channel configuration RAM error records 6 and 7

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-configuration-RAM-error-records-6-and-7>

### MHU Receiver FIFO channel configuration RAM error records 6 and 7

MHU Receiver FIFO channel configuration RAM error record 6 contains RAM ECC errors that are correctable. Receiver FIFO channel configuration RAM error record 7 contains RAM ECC errors that are uncorrectable.

If a correctable error is detected in the MHU Receiver FIFO channel configuration RAM, it is corrected and the error is reported in error record 6. For information about the error counters and interrupt generation options, see [Error recovery and fault handling interrupts](/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-recovery-and-fault-handling-interrupts?lang=en "You can assign a recorded correctable or uncorrectable error to the fault handling interrupt (fault_int signal) by setting the associated ERR<n>CTLR.FI register field. For more information, see either SRAS_ERR<n>CTLR or RRAS_ERR<n>CTLR.").

Correctable errors do not require software to take any action within the MHU. However, software can choose to track error locations in case a RAM row or column can be repaired, and the RAM has repair capability.

The following table lists the [RRAS\_ERR<>MISC1](/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-MISC1--Error-Record--n--Miscellaneous-Register-1--n---0---9?lang=en "Records additional information on reported error.") report data for MHU Receiver FIFO channel configuration RAM error records 6 and 7.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Receiver FIFO channel configuration RAM errors, records 6 and 7
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d35310e136" rowspan="1">
    <p>
     Record
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d35310e140" rowspan="1">
    <p>
     ERR&lt;n&gt;MISC1 data description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6 = Correctable
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bit location, bits [6:0]
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     7 = Uncorrectable
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     None
    </p>
   </td>
  </tr>
 </tbody>
</table>

For more information, see [FIFO channel error recovery procedure](/documentation/107612/0001/Functional-description-of-MHU-320AE/MHU-320AE-channels/FIFO-channels/FIFO-channel-error-recovery-procedure?lang=en "If an uncorrectable FIFO channel error occurs, then the data being transferred in this channel may have been corrupted and a recovery sequence needs to be performed by software to bring the FIFO channel back to a known state.").
