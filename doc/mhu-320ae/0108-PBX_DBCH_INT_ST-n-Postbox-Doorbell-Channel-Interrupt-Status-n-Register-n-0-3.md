# PBX_DBCH_INT_ST<n>, Postbox Doorbell Channel Interrupt Status n Register, n = 0 - 3

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-DBCH-INT-ST-n---Postbox-Doorbell-Channel-Interrupt-Status-n-Register--n---0---3>

### PBX\_DBCH\_INT\_ST<n>, Postbox Doorbell Channel Interrupt Status n Register, n = 0 - 3

Indicates whether there is an interrupt outstanding for a Doorbell Channel

PBX\_DBCH\_INT\_ST0 has status fields for Doorbell Channels 0 to 31

PBX\_DBCH\_INT\_ST1 has status fields for Doorbell Channels 32 to 63

PBX\_DBCH\_INT\_ST2 has status fields for Doorbell Channels 64 to 95

PBX\_DBCH\_INT\_ST3 has status fields for Doorbell Channels 96 to 127

### Configurations

This register is present only when DBE is implemented. Otherwise, direct accesses to PBX\_DBCH\_INT\_ST<n> are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (4 \* n) + 0x0400

### Bit descriptions

Figure 1. MHUS.PBX\_PBX\_DBCH\_INT\_ST<n> bit assignments

![mhus.pbx_pbx_dbch_int_st_n_ bit assignments](images/0108-PBX_DBCH_INT_ST-n-Postbox-Doorbell-Channel-Interrupt-Status-n-Register-n-0-3-img01.svg)

<table id="mhus_pbx_pbx_dbch_int_st_n__apbx_dbch_int_stn-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PBX_DBCH_INT_ST&lt;n&gt; bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d135817e170" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d135817e173" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d135817e176" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d135817e179" rowspan="1">
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
    DBCH_INT_ST&lt;x&gt;
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Doorbell Channel Interrupt Status
    </p>
    <p>
     Each bit indicates whether there is an interrupt outstanding for Doorbell Channel
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No interrupt outstanding for the Doorbell Channel or the Channel is not configured to factor into the Postbox Combined interrupt.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Interrupt outstanding for the Doorbell Channel and the Channel is configured to factor into the Postbox Combined interrupt.
      </p>
     </dd>
    </dl>
    <p>
     Any fields which are not assigned to a Channel are Reserved and treated as
     <span class="documents-archterm">
      RES0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d135817e256" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d135817e259" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d135817e262" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d135817e265" rowspan="1">
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
    (4 * n) + 0x0400
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PBX_DBCH_INT_ST&lt;n&gt;
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
