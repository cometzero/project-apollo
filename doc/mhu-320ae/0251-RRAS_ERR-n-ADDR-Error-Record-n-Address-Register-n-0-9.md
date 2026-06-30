# RRAS_ERR<n>ADDR, Error Record <n> Address Register, n = 0 - 9

Source: <https://developer.arm.com/documentation/107612/0001/Programmers-model-for-MHU-320AE/MHU-Receiver-registers/MHU-Receiver-RAS-register-summary/RRAS-ERR-n-ADDR--Error-Record--n--Address-Register--n---0---9>

### RRAS\_ERR<n>ADDR, Error Record <n> Address Register, n = 0 - 9

If an address is associated with a detected error, then it is written to ERR<n>ADDR when the error is recorded.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   64

Component
:   MHUR.RRAS

Register offset
:   (64 \* n) + 0x0018

### Bit descriptions

Figure 1. MHUR\_RRAS\_ERR<n>ADDR bit assignments

![mhur_rras_err_n_addr bit assignments](images/0251-RRAS_ERR-n-ADDR-Error-Record-n-Address-Register-n-0-9-img01.svg)

<table id="mhur_rras_err_n_addr__arras_errnaddr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   RRAS_ERR&lt;n&gt;ADDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d100953e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d100953e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d100953e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d100953e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Non-secure attribute. With RRAS_ERR&lt;n&gt;ADDR.NSE, indicates the physical address space of the recorded location.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       When RRAS_ERR&lt;n&gt;ADDR.NSE == 0: RRAS_ERR&lt;n&gt;ADDR.PADDR is a Secure address.
      </p>
      <p>
       When RRAS_ERR&lt;n&gt;ADDR.NSE == 1: RRAS_ERR&lt;n&gt;ADDR.PADDR is a Root address.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       When RRAS_ERR&lt;n&gt;ADDR.NSE == 0: RRAS_ERR&lt;n&gt;ADDR.PADDR is a Non-secure address.
      </p>
      <p>
       When RRAS_ERR&lt;n&gt;ADDR.NSE == 1: RRAS_ERR&lt;n&gt;ADDR.PADDR is a Realm address.
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
    [62]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Secure Incorrect. Indicates whether RRAS_ERR&lt;n&gt;ADDR.{NS, NSE} are valid.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       RRAS_ERR&lt;n&gt;ADDR.{NS, NSE} are correct. That is, they match the programmers' view of the physical address space for the recorded location.
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
    [61]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Address Incorrect. Indicates whether RRAS_ERR&lt;n&gt;ADDR.PADDR is a valid physical address.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       RRAS_ERR&lt;n&gt;ADDR.PADDR is a valid physical address. That is, it matches the programmers' view of the physical address for the recorded location.
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
    [60]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    VA
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Virtual Address. Indicates whether RRAS_ERR&lt;n&gt;ADDR.PADDR field is a virtual address.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       RRAS_ERR&lt;n&gt;ADDR.PADDR is not a virtual address.
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
    [59]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NSE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Physical Address Space. Together with RRAS_ERR&lt;n&gt;ADDR.NS, indicates the address space for RRAS_ERR&lt;n&gt;ADDR.PADDR.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [58:56]
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
    [55:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PADDR
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Physical Address. Address of the recorded location.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00000000000000
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
   <th class="documents-nocellnorowborder" colspan="1" id="d100953e433" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d100953e436" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d100953e439" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d100953e442" rowspan="1">
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
    (64 * n) + 0x0018
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    RRAS_ERR&lt;n&gt;ADDR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>
