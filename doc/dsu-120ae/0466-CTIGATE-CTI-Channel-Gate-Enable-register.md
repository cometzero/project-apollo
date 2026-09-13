# CTIGATE, CTI Channel Gate Enable register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIGATE--CTI-Channel-Gate-Enable-register>

### CTIGATE, CTI Channel Gate Enable register

Determines whether events on channels propagate through the CTM to other ECT components, or from the CTM into the CTI.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0x140

Access type
:   See bit descriptions

Reset value
:   0000 0000 0000 0000 0000 0000 0000 1111

### Bit descriptions

Figure 1. ext\_ctigate bit assignments

![ext_ctigate bit assignments](images/0466-CTIGATE-CTI-Channel-Gate-Enable-register-img01.svg)

<table id="urg1733415120839__actigate-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIGATE bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d206542e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d206542e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d206542e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d206542e146" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="urg1733415120839__31-4-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    GATE3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Channel &lt;x&gt; gate enable.
    </p>
    <p>
     Possible values of this bit are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Disable output and, if CTIDEVID.INOUT ==
       <span class="documents-g.number.bin">
        0b01
       </span>
       , input channel &lt;x&gt; propagation.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Enable output and, if CTIDEVID.INOUT ==
       <span class="documents-g.number.bin">
        0b01
       </span>
       , input channel &lt;x&gt; propagation.
      </p>
     </dd>
    </dl>
    <p>
     If GATE[x] is set to 0, no new events will be propagated to the ECT and any existing output channel events will be terminated.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="urg1733415120839__id-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    GATE2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Channel &lt;x&gt; gate enable.
    </p>
    <p>
     Possible values of this bit are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Disable output and, if CTIDEVID.INOUT ==
       <span class="documents-g.number.bin">
        0b01
       </span>
       , input channel &lt;x&gt; propagation.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Enable output and, if CTIDEVID.INOUT ==
       <span class="documents-g.number.bin">
        0b01
       </span>
       , input channel &lt;x&gt; propagation.
      </p>
     </dd>
    </dl>
    <p>
     If GATE[x] is set to 0, no new events will be propagated to the ECT and any existing output channel events will be terminated.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="urg1733415120839__id-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    GATE1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Channel &lt;x&gt; gate enable.
    </p>
    <p>
     Possible values of this bit are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Disable output and, if CTIDEVID.INOUT ==
       <span class="documents-g.number.bin">
        0b01
       </span>
       , input channel &lt;x&gt; propagation.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Enable output and, if CTIDEVID.INOUT ==
       <span class="documents-g.number.bin">
        0b01
       </span>
       , input channel &lt;x&gt; propagation.
      </p>
     </dd>
    </dl>
    <p>
     If GATE[x] is set to 0, no new events will be propagated to the ECT and any existing output channel events will be terminated.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="urg1733415120839__id-1-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    GATE0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Channel &lt;x&gt; gate enable.
    </p>
    <p>
     Possible values of this bit are:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Disable output and, if CTIDEVID.INOUT ==
       <span class="documents-g.number.bin">
        0b01
       </span>
       , input channel &lt;x&gt; propagation.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Enable output and, if CTIDEVID.INOUT ==
       <span class="documents-g.number.bin">
        0b01
       </span>
       , input channel &lt;x&gt; propagation.
      </p>
     </dd>
    </dl>
    <p>
     If GATE[x] is set to 0, no new events will be propagated to the ECT and any existing output channel events will be terminated.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="urg1733415120839__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
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
   <th class="documents-nocellnorowborder" colspan="1" id="d206542e380" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d206542e383" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d206542e386" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d206542e389" rowspan="1">
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
    0x140
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIGATE
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

When SoftwareLockStatus()
:   RO

When !SoftwareLockStatus()
:   RW
