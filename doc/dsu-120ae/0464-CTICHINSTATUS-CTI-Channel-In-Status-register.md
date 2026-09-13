# CTICHINSTATUS, CTI Channel In Status register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTICHINSTATUS--CTI-Channel-In-Status-register>

### CTICHINSTATUS, CTI Channel In Status register

Provides the raw status of the ECT channel inputs to the CTI.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0x138

Access type
:   RO

Reset value
:   0000 0000 0000 0000 0000 0000 0000 0000

### Bit descriptions

Figure 1. ext\_ctichinstatus bit assignments

![ext_ctichinstatus bit assignments](images/0464-CTICHINSTATUS-CTI-Channel-In-Status-register-img01.svg)

<table id="gxv1733415118574__actichinstatus-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTICHINSTATUS bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d110658e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d110658e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d110658e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d110658e146" rowspan="1">
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
     RAZ
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gxv1733415118574__31-4-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CHIN3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input channel &lt;n&gt; status.
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
       Input channel &lt;n&gt; is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Input channel &lt;n&gt; is active.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gxv1733415118574__id-3-reset" rowspan="1">
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
    CHIN2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input channel &lt;n&gt; status.
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
       Input channel &lt;n&gt; is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Input channel &lt;n&gt; is active.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gxv1733415118574__id-2-reset" rowspan="1">
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
    CHIN1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input channel &lt;n&gt; status.
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
       Input channel &lt;n&gt; is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Input channel &lt;n&gt; is active.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gxv1733415118574__id-1-reset" rowspan="1">
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
    CHIN0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Input channel &lt;n&gt; status.
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
       Input channel &lt;n&gt; is inactive.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Input channel &lt;n&gt; is active.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="gxv1733415118574__id-0-reset" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d110658e348" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d110658e351" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d110658e354" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d110658e357" rowspan="1">
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
    0x138
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTICHINSTATUS
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
