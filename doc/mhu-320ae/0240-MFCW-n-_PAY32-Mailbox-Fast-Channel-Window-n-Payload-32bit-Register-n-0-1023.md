# MFCW<n>_PAY32, Mailbox Fast Channel Window <n> Payload 32bit Register, n = 0 - 1023

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFCW-n--PAY32--Mailbox-Fast-Channel-Window--n--Payload-32bit-Register--n---0---1023>

### MFCW<n>\_PAY32, Mailbox Fast Channel Window <n> Payload 32bit Register, n = 0 - 1023

Access to payload of Fast Channel <n>

Arm recommends that accesses to these registers are atomic.

This is the 32bit version of the MFCW<n>\_PAY registers

### Configurations

This register is present only when FCE is implemented and FCH\_WS == 0x20. Otherwise, direct accesses to MFCW<n>\_PAY32 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offsets
:   (4 \* n) + 0x3000

### Bit descriptions

Figure 1. MFCW<n>\_PAY32\_MFCW<n>\_PAY32 bit assignments

![mfcw_n__pay32_mfcw_n__pay32 bit assignments](images/0240-MFCW-n-_PAY32-Mailbox-Fast-Channel-Window-n-Payload-32bit-Register-n-0-1023-img01.svg)

<table id="mfcw_n__pay32_mfcw_n__pay32__amfcwn_pay32-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MFCW&lt;n&gt;_PAY32 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d53222e165" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53222e168" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53222e171" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d53222e174" rowspan="1">
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
     Payload for Channel &lt;n&gt;
    </p>
    <p>
     A write to this register sets the value of the payload
    </p>
    <p>
     A read to this register:
    </p>
    <ul>
     <li>
      <p>
       returns the current value of the payload
      </p>
     </li>
     <li>
      <p>
       acknowledges the Transfer
      </p>
     </li>
     <li>
      <p>
       clears the Transfer interrupt for the Channel, if it is set
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mfcw_n__pay32_mfcw_n__pay32__bits-31-0-reset-18">
     32{x}
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
   <th class="documents-nocellnorowborder" colspan="1" id="d53222e256" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53222e259" rowspan="1">
    Offset
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d53222e262" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MFCW&lt;n&gt;_PAY32
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [(4 * n) + 0x3000]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    1023:0
   </td>
  </tr>
 </tbody>
</table>
