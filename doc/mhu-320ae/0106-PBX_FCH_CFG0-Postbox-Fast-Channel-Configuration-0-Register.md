# PBX_FCH_CFG0, Postbox Fast Channel Configuration 0 Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PBX-FCH-CFG0--Postbox-Fast-Channel-Configuration-0-Register>

### PBX\_FCH\_CFG0, Postbox Fast Channel Configuration 0 Register

Returns fast channel configuration information

### Configurations

This register is present only when FCE is implemented. Otherwise, direct accesses to PBX\_FCH\_CFG0 are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   0x0040

### Bit descriptions

Figure 1. MHUS.PBX\_PBX\_FCH\_CFG0 bit assignments

![mhus.pbx_pbx_fch_cfg0 bit assignments](images/0106-PBX_FCH_CFG0-Postbox-Fast-Channel-Configuration-0-Register-img01.svg)

<table id="mhus_pbx_pbx_fch_cfg0__apbx_fch_cfg0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PBX_FCH_CFG0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d114479e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d114479e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d114479e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d114479e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:29]
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
    [28:21]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FCH_WS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fast Channel Word Size
    </p>
    <p>
     Number of bits each Fast Channel implements.
    </p>
    <p>
     The value must be the same as MBX_FCH_CFG0.FCH_WS.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00100000
      </span>
     </dt>
     <dd>
      <p>
       Fast Channel word size is 32-bits
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01000000
      </span>
     </dt>
     <dd>
      <p>
       Fast Channel word size is 64-bits
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="mhus_pbx_pbx_fch_cfg0__id-28-21-reset-1" rowspan="1">
    The reset values can be the following:
    <span class="documents-g.number.bin">
     0b00100000
    </span>
    ,
    <span class="documents-g.number.bin">
     0b01000000
    </span>
    , respective to the value.
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [20:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NUM_FCH_PER_FCG
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Number of Fast Channels per Fast Channel Group for the Postbox
    </p>
    <dl>
     <dt class="documents-dlterm">
      0b00000..0b11111
     </dt>
     <dd>
      Number of Fast Channels per Fast Channel Group is N+1, where N is the value of this field
     </dd>
    </dl>
    <p>
     The number of Fast Channels in the last Fast Channel Group can be less than the value in this field if the value of NUM_FCH is not a multiple of the number of Fast Channels per Fast Channel Group.
    </p>
    <p>
     All other values are Reserved
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The reset value for this field depends on the MHU configuration.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:11]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NUM_FCG
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Number of Fast Channel Groups for the Postbox
    </p>
    <dl>
     <dt class="documents-dlterm">
      0b00000..0b11111
     </dt>
     <dd>
      Number of Fast Channel Groups is N+1, where N is the value of this field
     </dd>
    </dl>
    <p>
     The legal values for this field are 0-31
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The reset value for this field depends on the MHU configuration.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [10]
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
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [9:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    NUM_FCH
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of Fast Channels in the Postbox
    </p>
    <dl>
     <dt class="documents-dlterm">
      FCH_WS == 0x40
     </dt>
     <dd>
      <dl>
       <dt class="documents-dlterm">
        0b0000000000..0b0111111111
       </dt>
       <dd>
        Number of FCH is N+1, where N is the value of this field
       </dd>
      </dl>
     </dd>
     <dt class="documents-dlterm">
      FCH_WS == 0x20
     </dt>
     <dd>
      <dl>
       <dt class="documents-dlterm">
        0b0000000000..0b1111111111
       </dt>
       <dd>
        Number of FCH is N+1, where N is the value of this field
       </dd>
      </dl>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The reset value for this field depends on the MHU configuration.
    </p>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d114479e417" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d114479e420" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d114479e423" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d114479e426" rowspan="1">
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
    0x0040
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PBX_FCH_CFG0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
