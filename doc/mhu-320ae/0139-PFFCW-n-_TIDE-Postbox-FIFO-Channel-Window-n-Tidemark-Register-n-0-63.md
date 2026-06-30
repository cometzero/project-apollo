# PFFCW<n>_TIDE, Postbox FIFO Channel Window <n> Tidemark Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--TIDE--Postbox-FIFO-Channel-Window--n--Tidemark-Register--n---0---63>

### PFFCW<n>\_TIDE, Postbox FIFO Channel Window <n> Tidemark Register, n = 0 - 63

Allows configuration of the low and high tidemark thresholds for the Sender tidemark events

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to PFFCW<n>\_TIDE are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (64 \* n) + 0x202C

### Bit descriptions

Figure 1. EXT\_PFFCW<n>\_TIDE bit assignments

![ext_pffcw_n__tide bit assignments](images/0139-PFFCW-n-_TIDE-Postbox-FIFO-Channel-Window-n-Tidemark-Register-n-0-63-img01.svg)

<table id="ext_pffcw_n__tide__apffcwn_tide-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFFCW&lt;n&gt;_TIDE bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d10721e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10721e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d10721e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d10721e163" rowspan="1">
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
    HIGH
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     High Tide Mark.
    </p>
    <p>
     Threshold value used in the generation of the Sender FIFO High Tide event.
    </p>
    <p>
     The event is generated when a push to the FIFO occurs, and the following are both true:
    </p>
    <ul>
     <li>
      <p>
       The FIFO fill level before the push was less than or equal to the value of this field.
      </p>
     </li>
     <li>
      <p>
       The FIFO fill level after the push is greater than the value of this field.
      </p>
     </li>
    </ul>
    <p>
     The upper and lower offset of this field depend on the configuration of the MHU.
    </p>
    <p>
     The upper offset of this field is equal to clog2(FFCH_DEPTH)+15
    </p>
    <p>
     The lower offset of this field depends on the supported access sizes to PFFCW&lt;n&gt;_PAY register as follows:
    </p>
    <ul>
     <li>
      <p>
       When PBX_FFCH_CFG.P8BA_SPT is
       <span class="documents-g.number.bin">
        0b1
       </span>
       , the lower offset is 16.
      </p>
     </li>
     <li>
      <p>
       When PBX_FFCH_CFG.P8BA_SPT is
       <span class="documents-g.number.bin">
        0b0
       </span>
       and PBX_FFCH_CFG.P16BA_SPT is
       <span class="documents-g.number.bin">
        0b1
       </span>
       , the lower offset is 17.
      </p>
     </li>
     <li>
      <p>
       When PBX_FFCH_CFG.P{8/16}BA_SPT are both
       <span class="documents-g.number.bin">
        0b0
       </span>
       and PBX_FFCH_CFG.P32BA_SPT is
       <span class="documents-g.number.bin">
        0b1
       </span>
       , the lower offset is 18.
      </p>
     </li>
     <li>
      <p>
       When PBX_FFCH_CFG.P{8/16/32}BA_SPT are all
       <span class="documents-g.number.bin">
        0b0
       </span>
       and PBX_FFCH_CFG.P64BA_SPT is
       <span class="documents-g.number.bin">
        0b1
       </span>
       , the lower offset is 19.
      </p>
     </li>
    </ul>
    <p>
     Any offsets above the upper offset or below the lower offset are
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     If the upper offset is less than the lower offset, the entire field is
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     In all cases the value of this field includes the
     <span class="documents-archterm">
      RES0
     </span>
     offsets for calculation in the Sender High Tide event.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See field description.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:10]
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
    LOW
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Low Tide Mark
    </p>
    <p>
     Threshold value used in the generation of the Sender FIFO Low Tide event
    </p>
    <p>
     The event is generated when a pop to the FIFO occurs, and the following are both true:
    </p>
    <ul>
     <li>
      <p>
       The FIFO fill level before the pop was greater than the value of this field
      </p>
     </li>
     <li>
      <p>
       The FIFO fill level after the pop is less than or equal the value of this field
      </p>
     </li>
    </ul>
    <p>
     The upper and lower offset of this field depend on the configuration of the MHU.
    </p>
    <p>
     The upper offset of this field is equal to clog2(FFCH_DEPTH)-1
    </p>
    <p>
     The lower offset of this field depends on the supported access sizes to PFFCW&lt;n&gt;_PAY register as follows:
    </p>
    <ul>
     <li>
      <p>
       When PBX_FFCH_CFG.P8BA_SPT is
       <span class="documents-g.number.bin">
        0b1
       </span>
       , the lower offset is 0
      </p>
     </li>
     <li>
      <p>
       When PBX_FFCH_CFG.P8BA_SPT is
       <span class="documents-g.number.bin">
        0b0
       </span>
       and PBX_FFCH_CFG.P16BA_SPT is
       <span class="documents-g.number.bin">
        0b1
       </span>
       , the lower offset is 1
      </p>
     </li>
     <li>
      <p>
       When PBX_FFCH_CFG.P{8/16}BA_SPT are both
       <span class="documents-g.number.bin">
        0b0
       </span>
       and PBX_FFCH_CFG.P32BA_SPT is
       <span class="documents-g.number.bin">
        0b1
       </span>
       , the lower offset is 2
      </p>
     </li>
     <li>
      <p>
       When PBX_FFCH_CFG.P{8/16/32}BA_SPT are all
       <span class="documents-g.number.bin">
        0b0
       </span>
       and PBX_FFCH_CFG.P64BA_SPT is
       <span class="documents-g.number.bin">
        0b1
       </span>
       , the lower offset is 3
      </p>
     </li>
    </ul>
    <p>
     Any offsets above the upper offset or below the lower offset are
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     If the upper offset is less than the lower offset, the entire field is
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     In all cases the value of this field includes the
     <span class="documents-archterm">
      RES0
     </span>
     offsets for calculation in the Sender Low Tide event.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000000000
    </span>
   </td>
  </tr>
 </tbody>
</table>
