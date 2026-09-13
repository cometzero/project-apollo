# CTITRIGOUTSTATUS, CTI Trigger Out Status register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTITRIGOUTSTATUS--CTI-Trigger-Out-Status-register>

### CTITRIGOUTSTATUS, CTI Trigger Out Status register

Provides the raw status of the trigger outputs after processing by trigger interface logic.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0x134

Access type
:   RO

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_ctitrigoutstatus bit assignments

![ext_ctitrigoutstatus bit assignments](images/0463-CTITRIGOUTSTATUS-CTI-Trigger-Out-Status-register-img01.svg)

<table id="nhg1733415117389__actitrigoutstatus-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTITRIGOUTSTATUS bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d342261e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d342261e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d342261e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d342261e146" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__31-10-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TROUT9
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-9-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TROUT8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TROUT7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-7-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TROUT6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-6-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TROUT5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-5-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TROUT4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TROUT3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    TROUT2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-2-reset" rowspan="1">
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
    TROUT1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nhg1733415117389__id-1-reset" rowspan="1">
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
    TROUT0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Trigger output &lt;n&gt; status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Output trigger n is active.
      </p>
     </dd>
    </dl>
    <p>
     Otherwise when n &lt; N TROUT&lt;n&gt; is
     <span class="documents-archterm">
      RAZ
     </span>
     .
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="nhg1733415117389__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d342261e801" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d342261e804" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d342261e807" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d342261e810" rowspan="1">
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
    0x134
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTITRIGOUTSTATUS
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
