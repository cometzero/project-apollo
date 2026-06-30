# PFCW<n>_PAY64, Postbox Fast Channel Window <n> Payload 64bit Register, n = 0 - 511

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFCW-n--PAY64--Postbox-Fast-Channel-Window--n--Payload-64bit-Register--n---0---511>

### PFCW<n>\_PAY64, Postbox Fast Channel Window <n> Payload 64bit Register, n = 0 - 511

Access to payload of Fast Channel <n>

Arm recommends that accesses to these registers are atomic.

This is the 64bit version of the PFCW<n>\_PAY registers

### Configurations

This register is present only when FCE is implemented and FCH\_WS == 0x40. Otherwise, direct accesses to PFCW<n>\_PAY64 are RAZ/WI.

### Attributes

Width
:   64

Component
:   MHUS.PBX

Register offsets
:   (8 \* n) + 0x3000

### Bit descriptions

Figure 1. PFCW<n>\_PAY64\_PFCW<n>\_PAY64 bit assignments

![pfcw_n__pay64_pfcw_n__pay64 bit assignments](images/0141-PFCW-n-_PAY64-Postbox-Fast-Channel-Window-n-Payload-64bit-Register-n-0-511-img01.svg)

<table id="pfcw_n__pay64_pfcw_n__pay64__apfcwn_pay64-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFCW&lt;n&gt;_PAY64 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d103884e162" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103884e165" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103884e168" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d103884e171" rowspan="1">
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
    <code id="pfcw_n__pay64_pfcw_n__pay64__bits-63-0-reset-1">
     64{x}
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
   <th class="documents-nocellnorowborder" colspan="1" id="d103884e230" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d103884e233" rowspan="1">
    Offset
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d103884e236" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PFCW&lt;n&gt;_PAY64
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [(8 * n) + 0x3000]
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    511:0
   </td>
  </tr>
 </tbody>
</table>
