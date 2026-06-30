# PFFCW<n>_INT_ST, Postbox FIFO Channel Window <n> Interrupt Status Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--INT-ST--Postbox-FIFO-Channel-Window--n--Interrupt-Status-Register--n---0---63>

### PFFCW<n>\_INT\_ST, Postbox FIFO Channel Window <n> Interrupt Status Register, n = 0 - 63

Returns FIFO channel interrupt status

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to PFFCW<n>\_INT\_ST are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (64 \* n) + 0x2010

### Bit descriptions

Shows the status of the events of the DBCH

Figure 1. MHUS.PBX\_PFFCW<n>\_INT\_ST bit assignments

![mhus.pbx_pffcw_n__int_st bit assignments](images/0133-PFFCW-n-_INT_ST-Postbox-FIFO-Channel-Window-n-Interrupt-Status-Register-n-0-63-img01.svg)

<table id="mhus_pbx_pffcw_n__int_st__apffcwn_int_st-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFFCW&lt;n&gt;_INT_ST bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d57745e157" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57745e160" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57745e163" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d57745e166" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No FIFO flush event has occurred
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FIFO flush event has occurred
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30:3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FHT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No FIFO High Tidemark event has occurred
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FIFO High Tidemark event has occurred
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FLT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No FIFO Low Tidemark event has occurred
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FIFO Low Tidemark event has occurred
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    TFR_ACK
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No Transfer Acknowledge event
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Transfer Acknowledge event
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
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
   <th class="documents-nocellnorowborder" colspan="1" id="d57745e427" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57745e430" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d57745e433" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d57745e436" rowspan="1">
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
    (64 * n) + 0x2010
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PFFCW&lt;n&gt;_INT_ST
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
