# PFFCW<n>_ACK_CNT, Postbox FIFO Channel Window <n> Acknowledge Counter Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ACK-CNT--Postbox-FIFO-Channel-Window--n--Acknowledge-Counter-Register--n---0---63>

### PFFCW<n>\_ACK\_CNT, Postbox FIFO Channel Window <n> Acknowledge Counter Register, n = 0 - 63

Allows determining the number of acknowledged FIFO channel transfers

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to PFFCW<n>\_ACK\_CNT are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (64 \* n) + 0x2028

### Bit descriptions

Figure 1. MHUS.PBX\_PFFCW<n>\_ACK\_CNT bit assignments

![mhus.pbx_pffcw_n__ack_cnt bit assignments](images/0138-PFFCW-n-_ACK_CNT-Postbox-FIFO-Channel-Window-n-Acknowledge-Counter-Register-n-0-63-img01.svg)

<table id="mhus_pbx_pffcw_n__ack_cnt__apffcwn_ack_cnt-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFFCW&lt;n&gt;_ACK_CNT bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d41244e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACK_CNT_OVRFLW
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicate whether the Acknowledge counter has overflown.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Acknowledge counter has not overflown
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Acknowledge counter has overflown
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
    [10:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ACK_CNT
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Count of the number of Transfer Acknowledge events which have occurred since the last time the register was read.
    </p>
    <p>
     When value of ACK_CNT_OVRFLW is set to 1 the value in this field no longer provides an accurate count of the number of Transfer Acknowledge events.
    </p>
    <p>
     The maximum value of this field is calculated by 2
     <sup>
      clog2((FFCH_DEPTH/min_transfer_size)+1)
     </sup>
     - 1.
    </p>
    <p>
     Where min_transfer_size is minimum size of a Transfer in bytes which the Sender can send.
    </p>
    <p>
     The value of min_transfer_size is determined from the values of the P{8/16/32/64}BA_SPT fields in the PBX_FFCH_CFG0 register.
     <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ACK-CNT--Postbox-FIFO-Channel-Window--n--Acknowledge-Counter-Register--n---0---63?lang=en#mhus_pbx_pffcw_n__ack_cnt__mhus_pbx_pffcw_n__ack_cnt_p8basptdescriptiondescription" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--ACK-CNT--Postbox-FIFO-Channel-Window--n--Acknowledge-Counter-Register--n---0---63?lang=en#mhus_pbx_pffcw_n__ack_cnt__mhus_pbx_pffcw_n__ack_cnt_p8basptdescriptiondescription">
      P8BA_SPT description
     </a>
    </p>
    <p>
     When the counter reaches maximum value and a new Acknowledge occurs
    </p>
    <p>
     the ACK_CNT_OVRFLW is set to
     <span class="documents-g.number.bin">
      0b1
     </span>
     and the ACK_CNT field wraps around
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b00000000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

<table id="mhus_pbx_pffcw_n__ack_cnt__mhus_pbx_pffcw_n__ack_cnt_p8basptdescriptiondescription">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   P8BA_SPT description
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e315" rowspan="1">
    P8BA_SPT
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e318" rowspan="1">
    P16BA_SPT
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e321" rowspan="1">
    P32BA_SPT
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e324" rowspan="1">
    P64BA_SPT
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d41244e327" rowspan="1">
    Minimum Transfer Size (Bytes)
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    X
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    X
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    X
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    1
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    X
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    X
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    2
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    X
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    4
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    1
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    8
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
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
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e430" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e433" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d41244e436" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d41244e439" rowspan="1">
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
    (64 * n) + 0x2028
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PFFCW&lt;n&gt;_ACK_CNT
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
