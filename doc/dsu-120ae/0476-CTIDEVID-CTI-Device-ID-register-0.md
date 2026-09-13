# CTIDEVID, CTI Device ID register 0

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIDEVID--CTI-Device-ID-register-0>

### CTIDEVID, CTI Device ID register 0

Describes the CTI component to the debugger.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0xFC8

Access type
:   RO

Reset value
:   ```
    xxxx xx01 xx00 0100 xx00 1010 xxxx xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ctidevid bit assignments

![ext_ctidevid bit assignments](images/0476-CTIDEVID-CTI-Device-ID-register-0-img01.svg)

<table id="lbh1733415131315__actidevid-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIDEVID bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d12177e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12177e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12177e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d12177e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="lbh1733415131315__31-26-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [25:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INOUT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input/output options. Indicates presence of the input gate.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       ext-CTIGATE does not mask propagation of input events from external channels.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       ext-CTIGATE masks propagation of input events from external channels.
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lbh1733415131315__id-25-24-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b01
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:22]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lbh1733415131315__23-22-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [21:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NUMCHAN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Number of ECT channels implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000100
      </span>
     </dt>
     <dd>
      <p>
       4 channels (0..3) implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lbh1733415131315__id-21-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b000100
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:14]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lbh1733415131315__15-14-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [13:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NUMTRIG
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Number of triggers implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b001010
      </span>
     </dt>
     <dd>
      <p>
       10 triggers (0..9) implemented.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lbh1733415131315__id-13-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b001010
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lbh1733415131315__7-5-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [4:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    EXTMUXNUM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Number of multiplexors available on triggers. This value is used in conjunction with External Control register, ext-ASICCTL.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000
      </span>
     </dt>
     <dd>
      <p>
       No multiplexors implemented. ext-ASICCTL is unused.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="lbh1733415131315__id-4-0-reset" rowspan="1">
    <code>
     5{x}
    </code>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d12177e442" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12177e445" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d12177e448" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d12177e451" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTI
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0xFC8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIDEVID
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
