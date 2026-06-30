# PBX_FFCH_INT_ST<n>, Postbox FIFO Channel Interrupt Status n Register, n = 0 - 1

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FFCH-INT-ST-n---Postbox-FIFO-Channel-Interrupt-Status-n-Register--n---0---1>

### PBX\_FFCH\_INT\_ST<n>, Postbox FIFO Channel Interrupt Status n Register, n = 0 - 1

Indicates whether there is an interrupt outstanding for the FIFO Channel.

PBX\_FFCH\_INT\_ST0 has status fields for FIFO Channels 0 to 31

PBX\_FFCH\_INT\_ST1 has status fields for FIFO Channels 32 to 63

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to PBX\_FFCH\_INT\_ST<n> are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (4 \* n) + 0x0410

### Bit descriptions

Figure 1. MHUS.PBX\_PBX\_FFCH\_INT\_ST<n> bit assignments

![mhus.pbx_pbx_ffch_int_st_n_ bit assignments](images/0109-PBX_FFCH_INT_ST-n-Postbox-FIFO-Channel-Interrupt-Status-n-Register-n-0-1-img01.svg)

<table id="mhus_pbx_pbx_ffch_int_st_n__apbx_ffch_int_stn-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PBX_FFCH_INT_ST&lt;n&gt; bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d35002e164" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d35002e167" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d35002e170" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d35002e173" rowspan="1">
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
    FFCH_INT_ST&lt;x&gt;
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     FIFO Channel Interrupt Status
    </p>
    <p>
     Each bit indicates whether there is an interrupt outstanding for the FIFO Channel
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No interrupt outstanding for the FIFO Channel or the Channel is not configured to factor into the Postbox Combined interrupt.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Interrupt outstanding for the FIFO Channel and the Channel is configured to factor into the Postbox Combined interrupt.
      </p>
     </dd>
    </dl>
    <p>
     Any fields which are not assigned to a Channel are Reserved and treated as
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000
    </span>
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
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d35002e250" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d35002e253" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d35002e256" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d35002e259" rowspan="1">
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
    (4 * n) + 0x0410
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PBX_FFCH_INT_ST&lt;n&gt;
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
