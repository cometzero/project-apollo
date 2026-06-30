# Error handling records

Source: <https://developer.arm.com/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records>

### Error handling records

Both the MHU Sender and MHU Receiver have several error records. The range of available error handling records depends on the configuration of MHU-320AE.

> ### Note
>
> MHU-320AE follows the recommended RAS extension implementation of the MHUv3.0 architecture with the associated ERR<n>MISC0 register recording the following:
>
> - Transfer data lost: bit [16]
> - Impact zone: bits [14:13]
> - Channel type: bits [12:10]
> - Channel number: bits [9:0]

The following tables summarize the MHU-320AE error handling records in the MHU Sender and MHU Receiver. The Type column uses the following terms:

- Correctable Error (CE)
- Uncorrected latent, or restartable error (UEO)
- Uncorrected error, signalled, or recoverable error (UER)

The following table lists the MHU Sender error handling records.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MHU Sender error handling records
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
   <th class="documents-nocellnorowborder" colspan="1" id="d68899e143" rowspan="1">
    <p>
     Record
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d68899e147" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d68899e151" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d68899e155" rowspan="1">
    <p>
     Further information
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Software error in MHU Sender programming
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     UEO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-and-MHU-Receiver-software-error-records--Record-0?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-and-MHU-Receiver-software-error-records--Record-0?lang=en" title="Software error record 0 contains software errors that are uncorrectable both in the MHU Sender and MHU Receiver.">
      MHU Sender and MHU Receiver software error records, Record 0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncorrectable MHU Receiver errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     UER
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/Uncorrectable-MHU-Receiver-error-record-1-in-MHU-Sender?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/Uncorrectable-MHU-Receiver-error-record-1-in-MHU-Sender?lang=en" title="Error record 1 in the MHU Sender contains uncorrectable RAM errors that have been observed in the MHU Receiver. You can use this error record to let the MHU Sender software know that a particular channel has been corrupted, even if the corruption is not local, in case the MHU Sender software needs to take action. You can obtain the channel type and number information from SRAS_ERR1MISC0 register.">
      Uncorrectable MHU Receiver error record 1 in MHU Sender
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Correctable MHU Sender FIFO RAM errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-FIFO-channel-RAM-error-records-2-and-3?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-FIFO-channel-RAM-error-records-2-and-3?lang=en" title="MHU Sender FIFO channel RAM error record 2 contains RAM ECC errors that are correctable. MHU Sender FIFO channel RAM error record 3 contains RAM ECC errors that are uncorrectable.">
      MHU Sender FIFO channel RAM error records 2 and 3
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Uncorrectable MHU Sender FIFO RAM errors
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     UER
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-FIFO-channel-RAM-error-records-2-and-3?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-FIFO-channel-RAM-error-records-2-and-3?lang=en" title="MHU Sender FIFO channel RAM error record 2 contains RAM ECC errors that are correctable. MHU Sender FIFO channel RAM error record 3 contains RAM ECC errors that are uncorrectable.">
      MHU Sender FIFO channel RAM error records 2 and 3
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>

The following table lists the MHU Receiver error handling records.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Receiver error handling records
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
   <th class="documents-nocellnorowborder" colspan="1" id="d68899e286" rowspan="1">
    <p>
     Record
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d68899e290" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d68899e294" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d68899e298" rowspan="1">
    <p>
     Further information
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Software error in MHU Receiver programming
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     UEO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-and-MHU-Receiver-software-error-records--Record-0?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Sender-and-MHU-Receiver-software-error-records--Record-0?lang=en" title="Software error record 0 contains software errors that are uncorrectable both in the MHU Sender and MHU Receiver.">
      MHU Sender and MHU Receiver software error records, Record 0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncorrectable MHU Sender errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     UER
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/Uncorrectable-MHU-Sender-error-record-1-in-MHU-Receiver?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/Uncorrectable-MHU-Sender-error-record-1-in-MHU-Receiver?lang=en" title="Error record 1 in the MHU Receiver contains uncorrectable RAM errors that have been observed in the MHU Sender. The aim of this error record is to let the MHU Receiver software know that a particular channel has been corrupted in case it needs to take action, even if the corruption is not local. The channel type and number information can be obtained from RRAS_ERR1MISC0.">
      Uncorrectable MHU Sender error record 1 in MHU Receiver
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Correctable MHU Receiver doorbell RAM errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-doorbell-channel-RAM-error-records-2-and-3?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-doorbell-channel-RAM-error-records-2-and-3?lang=en" title="MHU Receiver doorbell channel RAM error record 2 contains RAM ECC errors that are correctable and record 3 contains RAM ECC errors that are uncorrectable.">
      MHU Receiver doorbell channel RAM error records 2 and 3
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncorrectable MHU Receiver doorbell RAM errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     UER
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-doorbell-channel-RAM-error-records-2-and-3?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-doorbell-channel-RAM-error-records-2-and-3?lang=en" title="MHU Receiver doorbell channel RAM error record 2 contains RAM ECC errors that are correctable and record 3 contains RAM ECC errors that are uncorrectable.">
      MHU Receiver doorbell channel RAM error records 2 and 3
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     4
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Correctable MHU Receiver fast channel RAM errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-fast-channel-RAM-error-records-4-and-5?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-fast-channel-RAM-error-records-4-and-5?lang=en" title="MHU Receiver fast channel RAM error record 4 contains RAM ECC errors that are correctable and record 5 contains RAM ECC errors that are uncorrectable.">
      MHU Receiver fast channel RAM error records 4 and 5
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     5
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncorrectable MHU Receiver fast channel RAM errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     UER
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-fast-channel-RAM-error-records-4-and-5?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-fast-channel-RAM-error-records-4-and-5?lang=en" title="MHU Receiver fast channel RAM error record 4 contains RAM ECC errors that are correctable and record 5 contains RAM ECC errors that are uncorrectable.">
      MHU Receiver fast channel RAM error records 4 and 5
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     6
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Correctable MHU Receiver FIFO configuration RAM errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-configuration-RAM-error-records-6-and-7?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-configuration-RAM-error-records-6-and-7?lang=en" title="MHU Receiver FIFO channel configuration RAM error record 6 contains RAM ECC errors that are correctable. Receiver FIFO channel configuration RAM error record 7 contains RAM ECC errors that are uncorrectable.">
      MHU Receiver FIFO channel configuration RAM error records 6 and 7
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     7
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncorrectable MHU Receiver FIFO configuration RAM errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     UER
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-configuration-RAM-error-records-6-and-7?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-configuration-RAM-error-records-6-and-7?lang=en" title="MHU Receiver FIFO channel configuration RAM error record 6 contains RAM ECC errors that are correctable. Receiver FIFO channel configuration RAM error record 7 contains RAM ECC errors that are uncorrectable.">
      MHU Receiver FIFO channel configuration RAM error records 6 and 7
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     8
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Correctable MHU Receiver FIFO data RAM errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CE
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-data-RAM-error-records-8-and-9?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-data-RAM-error-records-8-and-9?lang=en" title="MHU Receiver FIFO channel data RAM error record 8 contains RAM ECC errors that are correctable. Receiver FIFO channel data RAM error record 9 contains RAM ECC errors that are uncorrectable.">
      MHU Receiver FIFO channel data RAM error records 8 and 9
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     9
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Uncorrectable MHU Receiver FIFO data RAM errors
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     UER
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <a class="document-topic" document-topic-path="/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-data-RAM-error-records-8-and-9?lang=en" href="/documentation/107612/0001/Operations-of-MHU-320AE/Reliability--Accessibility--and-Serviceability/Error-handling-records/MHU-Receiver-FIFO-channel-data-RAM-error-records-8-and-9?lang=en" title="MHU Receiver FIFO channel data RAM error record 8 contains RAM ECC errors that are correctable. Receiver FIFO channel data RAM error record 9 contains RAM ECC errors that are uncorrectable.">
      MHU Receiver FIFO channel data RAM error records 8 and 9
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>
