# PFFCW<n>_FLG, Postbox FIFO Channel Window <n> Flag Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--FLG--Postbox-FIFO-Channel-Window--n--Flag-Register--n---0---63>

### PFFCW<n>\_FLG, Postbox FIFO Channel Window <n> Flag Register, n = 0 - 63

Provides access to the flags of the entry of the FIFO pointed to by the write pointer.

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to PFFCW<n>\_FLG are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (64 \* n) + 0x2008

### Bit descriptions

Figure 1. MHUS.PBX\_PFFCW<n>\_FLG bit assignments

![mhus.pbx_pffcw_n__flg bit assignments](images/0132-PFFCW-n-_FLG-Postbox-FIFO-Channel-Window-n-Flag-Register-n-0-63-img01.svg)

<table id="mhus_pbx_pffcw_n__flg__apffcwn_flg-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFFCW&lt;n&gt;_FLG bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d55972e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55972e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55972e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d55972e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:3]
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
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    EOT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     EOT flag.
    </p>
    <p>
     The EOT field indicates that the next push operation to the FIFO will contain the last byte of a Transfer.
    </p>
    <p>
     The behavior of this field depends on the value of the PFFCW&lt;n&gt;_CTRL.TDM field as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Next push operation does not contain the last byte of the Transfer
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Next push operation does contain the last byte of the Transfer
      </p>
     </dd>
    </dl>
    <p>
     For more information, see
     <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--FLG--Postbox-FIFO-Channel-Window--n--Flag-Register--n---0---63?lang=en#mhus_pbx_pffcw_n__flg__mhus_pbx_pffcw_n__flg_pffcwnctrltdmdescriptiondescription" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--FLG--Postbox-FIFO-Channel-Window--n--Flag-Register--n---0---63?lang=en#mhus_pbx_pffcw_n__flg__mhus_pbx_pffcw_n__flg_pffcwnctrltdmdescriptiondescription">
      PFFCW&lt;n&gt;_CTRL.TDM description
     </a>
     . The EOT flag is always associated with the last byte to be pushed onto the FIFO.
    </p>
    <p>
     When multiple bytes are pushed onto the FIFO via a single write to the PFFCW&lt;n&gt;_PAY register, which byte is associated with which fields depends on the value of the PFFCW&lt;n&gt;_CTRL.MSBF field as follows:
    </p>
    <ul>
     <li>
      <p>
       <span class="documents-g.number.bin">
        0b0
       </span>
       - LSB is associated with the SOT flag and MSB is associated with the EOT and ACK flags
      </p>
     </li>
     <li>
      <p>
       <span class="documents-g.number.bin">
        0b1
       </span>
       - MSB is associated with the SOT flag and LSB is associated with the EOT and ACK flags
      </p>
     </li>
    </ul>
    <p>
     Where B0 is the lowest offset in the PFFCW&lt;n&gt;_PAY accesses by the write and Bn is the highest offset in the PFFCW&lt;n&gt;_PAY accessed by the write.
    </p>
    <dl>
     <dt class="documents-dlterm">
      When PFFCW&lt;n&gt;_CTRL.TDM == '00'
     </dt>
     <dd>
      Access to this field is: RW
     </dd>
     <dt class="documents-dlterm">
      When PFFCW&lt;n&gt;_CTRL.TDM == '01' and (EOT field will be set to == '1' or SOT field will be set to == '1')
     </dt>
     <dd>
      Access to this field is: RW
     </dd>
     <dt class="documents-dlterm">
      When PFFCW&lt;n&gt;_CTRL.TDM == '01' and (EOT field will be set to == '0' and SOT field will be set to == '0')
     </dt>
     <dd>
      Access to this field is: RO
     </dd>
     <dt class="documents-dlterm">
      When PFFCW&lt;n&gt;_CTRL.TDM == '10'
     </dt>
     <dd>
      Access to this field is: RO
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
    SOT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SOT flag.
    </p>
    <p>
     The SOT flag indicates that the next push operation to the FIFO will contain the first byte of a Transfer.
    </p>
    <p>
     The behavior of this field depends on the value of the PFFCW&lt;n&gt;_CTRL.TDM field as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Next push operation does not contain the first byte of the Transfer
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Next push operation does contain the first byte of the Transfer
      </p>
     </dd>
    </dl>
    <p>
     For more information, see
     <a class="document-topic" document-topic-path="/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--FLG--Postbox-FIFO-Channel-Window--n--Flag-Register--n---0---63?lang=en#mhus_pbx_pffcw_n__flg__mhus_pbx_pffcw_n__flg_pffcwnctrltdmdescriptiondescription_2" href="/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--FLG--Postbox-FIFO-Channel-Window--n--Flag-Register--n---0---63?lang=en#mhus_pbx_pffcw_n__flg__mhus_pbx_pffcw_n__flg_pffcwnctrltdmdescriptiondescription_2">
      PFFCW&lt;n&gt;_CTRL.TDM description table 3
     </a>
     . The SOT flag is always associated with the first byte to be pushed onto the FIFO.
    </p>
    <p>
     When multiple bytes are pushed onto the FIFO via a single write to the PFFCW&lt;n&gt;_PAY register, which byte is associated with which fields depends on the value of the PFFCW&lt;n&gt;_CTRL.MSBF field as follows:
    </p>
    <ul>
     <li>
      <p>
       <span class="documents-g.number.bin">
        0b0
       </span>
       - LSB is associated with the SOT flag and MSB is associated with the EOT and ACK flags.
      </p>
     </li>
     <li>
      <p>
       <span class="documents-g.number.bin">
        0b1
       </span>
       - MSB is associated with the SOT flag and LSB is associated with the EOT and ACK flags.
      </p>
     </li>
    </ul>
    <p>
     Where B0 is the lowest offset in the PFFCW&lt;n&gt;_PAY accesses by the write and Bn is the highest offset in the PFFCW&lt;n&gt;_PAY accessed by the write.
    </p>
    <dl>
     <dt class="documents-dlterm">
      When PFFCW&lt;n&gt;_CTRL.TDM == '00'
     </dt>
     <dd>
      Access to this field is: RW
     </dd>
     <dt class="documents-dlterm">
      When PFFCW&lt;n&gt;_CTRL.TDM == '01' and (EOT field will be set to == '1' or SOT field will be set to == '1')
     </dt>
     <dd>
      Access to this field is: RW
     </dd>
     <dt class="documents-dlterm">
      When PFFCW&lt;n&gt;_CTRL.TDM == '01' and (EOT field will be set to == '0' and SOT field will be set to == '0')
     </dt>
     <dd>
      Access to this field is: RO
     </dd>
     <dt class="documents-dlterm">
      When PFFCW&lt;n&gt;_CTRL.TDM == '10'
     </dt>
     <dd>
      Access to this field is: RO
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
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ACK
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     ACK Flag.
    </p>
    <p>
     The ACK flag requests that when the Receiver pops the byte and the byte is the last byte of the Transfer, from the FIFO, a Transfer Acknowledge event is generated.
    </p>
    <p>
     The behavior of the ACK field is not effected by the value of PFFCW&lt;n&gt;_CTRL.TDM.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Entry is not requested to generate a Transfer Acknowledge event when popped from the FIFO
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Entry is requested to generate a Transfer Acknowledge event when popped from the FIFO
      </p>
     </dd>
    </dl>
    <p>
     The ACK flag is always associated with the same byte that is associated with the EOT flag.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
 </tbody>
</table>

<table id="mhus_pbx_pffcw_n__flg__mhus_pbx_pffcw_n__flg_pffcwnctrltdmdescriptiondescription">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   PFFCW&lt;n&gt;_CTRL.TDM description
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d55972e438" rowspan="1">
    PFFCW&lt;n&gt;_CTRL.TDM
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d55972e441" rowspan="1">
    Behavior of the EOT field
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Software manages the EOT field directly and hardware never changes the value. The access permission of this field is read-write
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b01
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The EOT field is set by software and hardware. The EOT is set to
    <span class="documents-g.number.bin">
     0b0
    </span>
    when PFFCW&lt;n&gt;_CTRL.TDM is set to
    <span class="documents-g.number.bin">
     0b01
    </span>
    and can only be written to if it or the SOT field is to be set to
    <span class="documents-g.number.bin">
     0b1
    </span>
    , otherwise the value remains unchanged. When one or more bytes are pushed onto the FIFO, the EOT field is set to
    <span class="documents-g.number.bin">
     0b0
    </span>
    irrespective of the value of the SOT or EOT fields before the push. The access permission of this field is read-write if either this field or the SOT field will be set to
    <span class="documents-g.number.bin">
     0b1
    </span>
    by the write, otherwise it is read-only.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The EOT field is managed by hardware. The EOT flag is set to
    <span class="documents-g.number.bin">
     0b0
    </span>
    when PFFCW&lt;n&gt;_CTRL.TDM is set to
    <span class="documents-g.number.bin">
     0b10
    </span>
    and is read-only. The EOT flag value toggles when one or more bytes are pushed onto the FIFO. The access permission of this field is read-only.
   </td>
  </tr>
 </tbody>
</table>

<table id="mhus_pbx_pffcw_n__flg__mhus_pbx_pffcw_n__flg_pffcwnctrltdmdescriptiondescription_2">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 3.
   </span>
   PFFCW&lt;n&gt;_CTRL.TDM description table 3
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d55972e516" rowspan="1">
    PFFCW&lt;n&gt;_CTRL.TDM
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d55972e519" rowspan="1">
    Behavior of the SOT field
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    Software manages the SOT field directly and hardware never changes the value. The access permission of this field is read-write.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b01
    </span>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    The SOT field is set by software and hardware. The SOT is set to
    <span class="documents-g.number.bin">
     0b1
    </span>
    when PFFCW&lt;n&gt;_CTRL.TDM is set to
    <span class="documents-g.number.bin">
     0b01
    </span>
    and can only be written to if it or the EOT field is to be set to
    <span class="documents-g.number.bin">
     0b1
    </span>
    , otherwise the value remains unchanged. When one or more bytes are pushed onto the FIFO, the SOT field value will be set to the value of the EOT field when the push occurred. The access permission of this field is read-write if either this field or the SOT field will be set to
    <span class="documents-g.number.bin">
     0b1
    </span>
    by the write, otherwise it is read-only.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
    </span>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    The SOT field is managed by hardware. The SOT flag is set to
    <span class="documents-g.number.bin">
     0b0
    </span>
    when PFFCW&lt;n&gt;_CTRL.TDM is set to
    <span class="documents-g.number.bin">
     0b10
    </span>
    and is read-only. The SOT flag value toggles when one or more bytes are pushed onto the FIFO. The access permission of this field is read-only.
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 4.
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
   <th class="documents-nocellnorowborder" colspan="1" id="d55972e601" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55972e604" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55972e607" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d55972e610" rowspan="1">
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
    (64 * n) + 0x2008
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PFFCW&lt;n&gt;_FLG
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
