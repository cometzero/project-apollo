# MFFCW<n>_INT_EN, Mailbox FIFO Channel Window <n> Interrupt Enable Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Mailbox-register-summary/MFFCW-n--INT-EN--Mailbox-FIFO-Channel-Window--n--Interrupt-Enable-Register--n---0---63>

### MFFCW<n>\_INT\_EN, Mailbox FIFO Channel Window <n> Interrupt Enable Register, n = 0 - 63

Register for configuring FIFO channel interrupt enables

This register shows the status of FIFO channel events.

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to MFFCW<n>\_INT\_EN are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.MBX

Register offset
:   (64 \* n) + 0x2018

### Bit descriptions

Figure 1. MHUR.MBX\_MFFCW<n>\_INT\_EN bit assignments

![mhur.mbx_mffcw_n__int_en bit assignments](images/0235-MFFCW-n-_INT_EN-Mailbox-FIFO-Channel-Window-n-Interrupt-Enable-Register-n-0-63-img01.svg)

<table id="mhur_mbx_mffcw_n__int_en__amffcwn_int_en-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MFFCW&lt;n&gt;_INT_EN bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d64896e160" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64896e163" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64896e166" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d64896e169" rowspan="1">
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
       FIFO flush events do not generate an interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FIFO flush events generate an interrupt
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
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
       FIFO High Tidemark events do not generate an interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FIFO High Tidemark events generate an interrupt
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
       FIFO Low Tidemark events do not generate an interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FIFO Low Tidemark events generate an interrupt
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
    TFR
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
       Transfer events do not generate an interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      Transfer events generate interrupts
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
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
   <th class="documents-nocellnorowborder" colspan="1" id="d64896e427" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64896e430" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d64896e433" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d64896e436" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.MBX
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    (64 * n) + 0x2018
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MFFCW&lt;n&gt;_INT_EN
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
