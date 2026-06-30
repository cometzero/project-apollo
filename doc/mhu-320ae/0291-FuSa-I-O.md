# FuSa I/O

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/FuSa-I-O>

### FuSa I/O

The MHU-320AE has extra signals for FuSa fault detection and control.

The following table lists the protection mechanism that MHU-320AE uses for each AMBA interface or signal type.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   AMBA interface FuSa ports
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d34042e102" rowspan="1">
    <p>
     Interface type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d34042e106" rowspan="1">
    <p>
     Protection mechanism
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     APB5
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     AMBA parity
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     AXI5-Stream interfaces between internal MHU blocks
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     AMBA parity, or CRC, or both
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     ACE5-Lite
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     AMBA parity added to all external ACE5-Lite interfaces, including communications interface, when configured to use ACE5-Lite instead of AXI5-Stream.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Q-Channel
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     AMBA parity
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Clock input signal
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Duplicated
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       *_chk
      </span>
     </span>
     signal
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reset input signal
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Duplicated
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       *_chk
      </span>
     </span>
     signal
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Non-AMBA input signal
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Odd parity
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       *_chk
      </span>
     </span>
     signal
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Non-AMBA output signal
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Odd parity
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       *_chk
      </span>
     </span>
     signal
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Interrupt outputs
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Odd parity
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       *_chk
      </span>
     </span>
     signal
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     External error interfaces
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Odd parity
     <span class="documents-g.signal.name">
      <span class="documents-keyword">
       *_chk
      </span>
     </span>
     signal
    </p>
   </td>
  </tr>
 </tbody>
</table>

For more information about the signals, see the Arm® CoreLink™ MHU-320AE Message Handling Unit Configuration and Integration Manual.
