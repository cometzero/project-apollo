# RRAS_ERRACR, Access Configuration Register

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERRACR--Access-Configuration-Register>

### RRAS\_ERRACR, Access Configuration Register

Controls visibility of error records.

### Configurations

This register is present only when TZE is implemented for the MHU Receiver. Otherwise, direct accesses to RRAS\_ERRACR are RAZ/WI.

### Attributes

Width
:   64

Component
:   MHUR.RRAS

Register offset
:   0x0E40

### Bit descriptions

Figure 1. MHUR\_RRAS\_ERRACR bit assignments

![mhur_rras_erracr bit assignments](images/0258-RRAS_ERRACR-Access-Configuration-Register-img01.svg)

<table id="mhur_rras_erracr__arras_erracr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RRAS_ERRACR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d48505e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48505e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48505e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d48505e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:32]
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
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    IMPL
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates RRAS_ERRACR is present.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       RRAS_ERRACR is present.
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
    [30:6]
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
    [5:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RLRA
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      When RME is implemented for the MHU Receiver
     </dt>
     <dd>
      <p>
       Realm Restricted Access. Controls Realm access to error records when RME is supported.
      </p>
     </dd>
     <dd class="documents-ddexpand">
      <dl>
       <dt class="documents-dlterm">
        <span class="documents-g.number.bin">
         0b00
        </span>
       </dt>
       <dd>
        <p>
         Realm access is disabled
        </p>
       </dd>
       <dt class="documents-dlterm">
        <span class="documents-g.number.bin">
         0b01
        </span>
       </dt>
       <dd>
        <p>
         Realm read access is enabled. Realm writes are ignored.
        </p>
       </dd>
       <dt class="documents-dlterm">
        <span class="documents-g.number.bin">
         0b11
        </span>
       </dt>
       <dd>
        <p>
         Realm read/write access is allowed.
        </p>
       </dd>
      </dl>
     </dd>
     <dd class="documents-ddexpand">
     </dd>
     <dt class="documents-dlterm">
      Otherwise
     </dt>
     <dd>
      RES0
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span id="mhur_rras_erracr__bits-5-4-reset-1">
     xx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3:2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SRA
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Secure Restricted Access. Controls Secure access to error records when RME is supported.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Secure access is disabled
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Secure read access is enabled. Realm writes are ignored.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Secure read/write access is allowed.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [1:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    NSRA
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Non-secure Restricted Access. Controls Non-secure access to error records when TZE is supported.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Non-secure access is disabled
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Non-secure read access is enabled. Realm writes are ignored.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Non-secure read/write access is allowed.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
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
   <th class="documents-nocellnorowborder" colspan="1" id="d48505e476" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48505e479" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d48505e482" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d48505e485" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MHUR.RRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x0E40
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RRAS_ERRACR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
