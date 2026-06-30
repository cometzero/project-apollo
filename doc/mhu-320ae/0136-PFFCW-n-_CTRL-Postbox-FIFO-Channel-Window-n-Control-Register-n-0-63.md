# PFFCW<n>_CTRL, Postbox FIFO Channel Window <n> Control Register, n = 0 - 63

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-Postbox-register-summary/PFFCW-n--CTRL--Postbox-FIFO-Channel-Window--n--Control-Register--n---0---63>

### PFFCW<n>\_CTRL, Postbox FIFO Channel Window <n> Control Register, n = 0 - 63

This register contains control bits for FIFO channels

### Configurations

This register is present only when FE is implemented. Otherwise, direct accesses to PFFCW<n>\_CTRL are RAZ/WI.

### Attributes

Width
:   32

Component
:   MHUS.PBX

Register offset
:   (64 \* n) + 0x2020

### Bit descriptions

Figure 1. MHUS.PBX\_PFFCW<n>\_CTRL bit assignments

![mhus.pbx_pffcw_n__ctrl bit assignments](images/0136-PFFCW-n-_CTRL-Postbox-FIFO-Channel-Window-n-Control-Register-n-0-63-img01.svg)

<table id="mhus_pbx_pffcw_n__ctrl__apffcwn_ctrl-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PFFCW&lt;n&gt;_CTRL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d63700e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d63700e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d63700e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d63700e163" rowspan="1">
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
    <p>
     FIFO Flush
    </p>
    <p>
     Request a flush of the FFCH
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No request to flush the FIFO
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Request to flush the FIFO
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
    [30:4]
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
    [3:2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TDM
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Transfer Delineation Mode
    </p>
    <p>
     Selects which Transfer delineation mode the MHU uses for the Channel
    </p>
    <p>
     Transfer delineation mode selects whether the MHU or software or a combination of both manages the SOT and EOT flags
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       None
      </p>
      <p>
       Software is responsible for managing the SOT and EOT flags
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Partial
      </p>
      <p>
       Flags are managed partially by software and partially by the MHU
      </p>
      <p>
       Upon selecting Partial Transfer delineation mode the PFFCW&lt;n&gt;_FLG.{SOT,EOT} fields are set to 0b1 and 0b0 respectively.
      </p>
      <p>
       No change occurs to the PFFCW&lt;n&gt;_FLG.ACK field
      </p>
      <p>
       To update either the PFFCW&lt;n&gt;_FLG.{SOT/EOT} fields, at least one of them must be set to 0b1, otherwise the update to those fields are ignored
      </p>
      <p>
       When a push operation occurs the SOT and EOT fields are updated as follows:
      </p>
      <ul>
       <li>
        <p>
         SOT field is set to value of the EOT field before the push
        </p>
       </li>
       <li>
        <p>
         EOT field is always set to 0b0
        </p>
       </li>
      </ul>
      <p>
       To update only the value of the PFFCW&lt;n&gt;_FLG.ACK field when using Partial Transfer delineation mode software should set both the SOT and EOT fields to 0b0 as this will keep EOT and SOT unchanged.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Auto
      </p>
      <p>
       Flags are fully managed by the MHU
      </p>
      <p>
       Upon selecting Auto Transfer delineation mode the PFFCW&lt;n&gt;_FLG.{SOT,EOT} fields are set to 0b1 and 0b0 respectively
      </p>
      <p>
       No change occurs to the PFFCW&lt;n&gt;_FLG.ACK field
      </p>
      <p>
       Any writes to the PFFCW&lt;n&gt;_FLG are ignored
      </p>
      <p>
       When a push operation occurs the values of the SOT and EOT fields toggle.
      </p>
      <p>
       To update the value of the PFFCW&lt;n&gt;_FLG.ACK field when using the Auto Transfer delineation mode software can write any value to the SOT and EOT fields as it will be ignored.
      </p>
     </dd>
    </dl>
    <p>
     All other values are Reserved
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MSBF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Most Significant Byte First
    </p>
    <p>
     Selects the order in which bytes are pushed onto the FIFO when multiple bytes are to be pushed due to a single write to the PFFCW&lt;n&gt;_PAY register
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Least Significant Byte first
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Most Significant Byte first
      </p>
     </dd>
    </dl>
    <p>
     FFCH are considered little-endian and the LSB is the lowest byte offset and the MSB is the highest byte offset within the access
    </p>
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
    PBX_COMB_EN
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
       FIFO Channel does not contribute to the Postbox Combined interrupt
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       FIFO Channel contributes to the Postbox Combined interrupt
      </p>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d63700e452" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d63700e455" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d63700e458" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d63700e461" rowspan="1">
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
    (64 * n) + 0x2020
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PFFCW&lt;n&gt;_CTRL
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
