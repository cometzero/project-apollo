# RSC_FFCH_CFG0, Receiver Security Control FIFO Channel Configuration 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-Security-Control-register-summary/RSC-FFCH-CFG0--Receiver-Security-Control-FIFO-Channel-Configuration-0-Register>

### RSC\_FFCH\_CFG0, Receiver Security Control FIFO Channel Configuration 0 Register

Returns FIFO channel configuration information

### Configurations

This register is present only when TZE is implemented for the MHUR and FE is implemented. Otherwise, direct accesses to RSC\_FFCH\_CFG0 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUR.RSC

Register offset
:   0x0030

### Bit descriptions

Figure 1. MHUR.RSC\_RSC\_FFCH\_CFG0 bit assignments

![mhur.rsc_rsc_ffch_cfg0 bit assignments](images/0176-RSC_FFCH_CFG0-Receiver-Security-Control-FIFO-Channel-Configuration-0-Register-img01.svg)

<table id="mhur_rsc_rsc_ffch_cfg0__arsc_ffch_cfg0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RSC_FFCH_CFG0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d55127e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55127e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55127e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d55127e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:26]
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
    [25:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FFCH_DEPTH
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     FIFO Channel Depth
    </p>
    <dl>
     <dt class="documents-dlterm">
      0b0000000000..0b1111111111
     </dt>
     <dd>
      FIFO depth is N+1 bytes, where N is the value of this field
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <code id="mhur_rsc_rsc_ffch_cfg0__bits-25-16-reset">
     10{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:12]
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
    M64BA_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Mailbox 64bit Access Support
    </p>
    <p>
     Whether the implementation of the MHU supports 64bit accesses to the following registers
    </p>
    <ul>
     <li>
      <p>
       MFFCW&lt;n&gt;_PAY
      </p>
     </li>
     <li>
      <p>
       MFFCW&lt;n&gt;_FLG
      </p>
     </li>
    </ul>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       64bit accesses are not supported
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       64bit accesses are supported
      </p>
     </dd>
    </dl>
    <p>
     Accesses must be aligned to an 64bit boundary
    </p>
    <p>
     The value of this field has no effect the supported access sizes to any other registers
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhur_rsc_rsc_ffch_cfg0__id-11-reset" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0
    </span>
    ,
    <span class="documents-g.number.bin">
     0b1
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    M32BA_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Mailbox 32bit Access Support
    </p>
    <p>
     Whether the implementation of the MHU supports 32bit accesses to the following registers
    </p>
    <ul>
     <li>
      <p>
       MFFCW&lt;n&gt;_PAY
      </p>
     </li>
     <li>
      <p>
       MFFCW&lt;n&gt;_FLG
      </p>
     </li>
    </ul>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       32bit accesses are not supported
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       32bit accesses are supported
      </p>
     </dd>
    </dl>
    <p>
     Accesses must be aligned to an 32bit boundary
    </p>
    <p>
     The value of this field has no effect the supported access sizes to any other registers
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhur_rsc_rsc_ffch_cfg0__id-10-reset" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0
    </span>
    ,
    <span class="documents-g.number.bin">
     0b1
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    M16BA_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Mailbox 16bit Access Support
    </p>
    <p>
     Whether the implementation of the MHU supports 32bit accesses to the following registers
    </p>
    <ul>
     <li>
      <p>
       MFFCW&lt;n&gt;_PAY
      </p>
     </li>
     <li>
      <p>
       MFFCW&lt;n&gt;_FLG
      </p>
     </li>
    </ul>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       16bit accesses are not supported
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       16bit accesses are supported
      </p>
     </dd>
    </dl>
    <p>
     Accesses must be aligned to an 16bit boundary
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhur_rsc_rsc_ffch_cfg0__id-9-reset" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0
    </span>
    ,
    <span class="documents-g.number.bin">
     0b1
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    M8BA_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Mailbox 8bit Access Support
    </p>
    <p>
     Whether the implementation of the MHU supports 8bit accesses to the following registers
    </p>
    <ul>
     <li>
      <p>
       MFFCW&lt;n&gt;_PAY
      </p>
     </li>
     <li>
      <p>
       MFFCW&lt;n&gt;_FLG
      </p>
     </li>
    </ul>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       8bit accesses are not supported
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       8bit accesses are supported
      </p>
     </dd>
    </dl>
    <p>
     Accesses must be aligned to an 8bit boundary
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhur_rsc_rsc_ffch_cfg0__id-8-reset" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b0
    </span>
    ,
    <span class="documents-g.number.bin">
     0b1
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    NUM_FFCH
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of FIFO Channels
    </p>
    <p>
     The number of FIFO Channels in the Mailbox.
    </p>
    <dl>
     <dt class="documents-dlterm">
      0b00000000..0b00111111
     </dt>
     <dd>
      Number of FIFO is N+1, where N is the value of this field
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <code id="mhur_rsc_rsc_ffch_cfg0__bits-7-0-reset-1">
     8{x}
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
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d55127e537" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55127e540" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d55127e543" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d55127e546" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.RSC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0030
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RSC_FFCH_CFG0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
