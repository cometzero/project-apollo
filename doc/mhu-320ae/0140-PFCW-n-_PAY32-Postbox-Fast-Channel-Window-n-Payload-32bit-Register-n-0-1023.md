# PFCW<n>_PAY32, Postbox Fast Channel Window <n> Payload 32bit Register, n = 0 - 1023

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFCW-n--PAY32--Postbox-Fast-Channel-Window--n--Payload-32bit-Register--n---0---1023>

### PFCW<n>\_PAY32, Postbox Fast Channel Window <n> Payload 32bit Register, n = 0 - 1023

Access to payload of Fast Channel <n>

Arm recommends that accesses to these registers are atomic.

This is the 32bit version of the PFCW<n>\_PAY registers

### Configurations

This register is present only when FCE is implemented and FCH\_WS == 0x20. Otherwise, direct accesses to PFCW<n>\_PAY32 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offsets
:   (4 \* n) + 0x3000

### Bit descriptions

Figure 1. PFCW<n>\_PAY32\_PFCW<n>\_PAY32 bit assignments

![pfcw_n__pay32_pfcw_n__pay32 bit assignments](images/0140-PFCW-n-_PAY32-Postbox-Fast-Channel-Window-n-Payload-32bit-Register-n-0-1023-img01.svg)

<table id="pfcw_n__pay32_pfcw_n__pay32__apfcwn_pay32-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFCW&lt;n&gt;_PAY32 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d69870e162" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69870e165" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69870e168" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d69870e171" rowspan="1">
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
     A write to this register sets the value of the payload and generates a Transfer event
    </p>
    <p>
     A read to this register returns the current value of the payload
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="pfcw_n__pay32_pfcw_n__pay32__bits-31-0-reset-11">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d69870e230" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d69870e233" rowspan="1">
    Offset
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d69870e236" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PFCW&lt;n&gt;_PAY32
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
