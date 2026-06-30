# PBX_FFCH_CFG0, Postbox FIFO Channel Configuration 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FFCH-CFG0--Postbox-FIFO-Channel-Configuration-0-Register>

### PBX\_FFCH\_CFG0, Postbox FIFO Channel Configuration 0 Register

Returns FIFO channel configuration information

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to PBX\_FFCH\_CFG0 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   0x0030

### Bit descriptions

Figure 1. MHUS.PBX\_PBX\_FFCH\_CFG0 bit assignments

![mhus.pbx_pbx_ffch_cfg0 bit assignments](images/0105-PBX_FFCH_CFG0-Postbox-FIFO-Channel-Configuration-0-Register-img01.svg)

<table id="mhus_pbx_pbx_ffch_cfg0__apbx_ffch_cfg0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PBX_FFCH_CFG0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d74806e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d74806e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d74806e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d74806e163" rowspan="1">
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
    <code id="mhus_pbx_pbx_ffch_cfg0__bits-25-16-reset-1">
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
    P64BA_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Postbox 64bit Access Support
    </p>
    <p>
     Whether the implementation of the MHU supports 64bit accesses to the PFFCW&lt;n&gt;_PAY register
    </p>
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
   <td class="documents-cell-norowborder" colspan="1" id="mhus_pbx_pbx_ffch_cfg0__id-11-reset-1" rowspan="1">
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
    P32BA_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Postbox 32bit Access Support
    </p>
    <p>
     Whether the implementation of the MHU supports 32bit accesses to the PFFCW&lt;n&gt;_PAY register
    </p>
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
   <td class="documents-cell-norowborder" colspan="1" id="mhus_pbx_pbx_ffch_cfg0__id-10-reset-1" rowspan="1">
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
    P16BA_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Postbox 16bit Access Support
    </p>
    <p>
     Whether the implementation of the MHU supports 16bit accesses to the PFFCW&lt;n&gt;_PAY register
    </p>
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
   <td class="documents-cell-norowborder" colspan="1" id="mhus_pbx_pbx_ffch_cfg0__id-9-reset-1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    P8BA_SPT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Postbox 8bit Access Support
    </p>
    <p>
     Whether the implementation of the MHU supports 8bit accesses to the PFFCW&lt;n&gt;_PAY register
    </p>
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
   <td class="documents-cell-norowborder" colspan="1" id="mhus_pbx_pbx_ffch_cfg0__id-8-reset-1" rowspan="1">
    <span class="documents-g.number.hex">
     0x0
    </span>
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
     The number of FIFO Channels in the Postbox.
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
    <code id="mhus_pbx_pbx_ffch_cfg0__bits-7-0-reset-7">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d74806e467" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d74806e470" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d74806e473" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d74806e476" rowspan="1">
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
    0x0030
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PBX_FFCH_CFG0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
