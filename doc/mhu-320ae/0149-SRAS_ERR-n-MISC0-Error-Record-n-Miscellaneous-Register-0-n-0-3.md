# SRAS_ERR<n>MISC0, Error Record <n> Miscellaneous Register 0, n = 0 - 3

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Sender-registers/MHU-Sender-RAS-register-summary/SRAS-ERR-n-MISC0--Error-Record--n--Miscellaneous-Register-0--n---0---3>

### SRAS\_ERR<n>MISC0, Error Record <n> Miscellaneous Register 0, n = 0 - 3

Records information on the reported error and error counters.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   MHUS.SRAS

Register offset
:   (64 \* n) + 0x0020

### Bit descriptions

Figure 1. MHUS\_SRAS\_ERR<n>MISC0 bit assignments

![mhus_sras_err_n_misc0 bit assignments](images/0149-SRAS_ERR-n-MISC0-Error-Record-n-Miscellaneous-Register-0-n-0-3-img01.svg)

<table id="mhus_sras_err_n_misc0__asras_errnmisc0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   SRAS_ERR&lt;n&gt;MISC0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d18876e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18876e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18876e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d18876e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:40]
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
    [39]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Sticky overflow bit. Set to 1 when SRAS_ERR&lt;n&gt;MISC0.CEC is incremented and wraps through zero.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Counter has not overflowed.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Counter has overflowed.
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
    [38:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Error count. Incremented on for each corrected or uncorrected error.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:17]
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
    [16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TL
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Transfer Lost.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Error has not caused loss of transfer data in channels within the impact zone.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Error may have caused loss of transfer data in channels within the impact zone.
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
    [15]
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
    [14:13]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    IZ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Impact Zone.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Global. Any channel may be affected by the recorded error.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Channel specific. Only a specific channel of a given type may be affected by the recorded error as indicated by SRAS_ERR&lt;n&gt;MISC0.CT and SRAS_ERR&lt;n&gt;MISC0.CN.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Channel type. Any channel of a specific type may be affected by the recorded error as indicated by SRAS_ERR&lt;n&gt;MISC0.CT.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [12:10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Channel Type.
     <span class="documents-archterm">
      RES0
     </span>
     when SRAS_ERR&lt;n&gt;MISC0.IZ == 2'b00
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000
      </span>
     </dt>
     <dd>
      <p>
       Doorbell channel.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001
      </span>
     </dt>
     <dd>
      <p>
       Fast channel.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       FIFO channel.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [9:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CN
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Channel Number.
     <span class="documents-archterm">
      RES0
     </span>
     when SRAS_ERR&lt;n&gt;MISC0.IZ != 2'b01
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
   <th class="documents-nocellnorowborder" colspan="1" id="d18876e554" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18876e557" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d18876e560" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d18876e563" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUS.SRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    (64 * n) + 0x0020
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SRAS_ERR&lt;n&gt;MISC0
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
