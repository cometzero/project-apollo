# CTIINEN7, CTI Input Trigger to Output Channel Enable registers

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINEN7--CTI-Input-Trigger-to-Output-Channel-Enable-registers>

### CTIINEN7, CTI Input Trigger to Output Channel Enable registers

Enables the signaling of an event on output channels when input trigger event n is received by the CTI.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0x3C

Access type
:   See bit descriptions

Reset value
:   ```
    0000 0000 0000 0000 0000 0000 0000 xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ctiinen7 bit assignments

![ext_ctiinen7 bit assignments](images/0449-CTIINEN7-CTI-Input-Trigger-to-Output-Channel-Enable-registers-img01.svg)

<table id="lsh1733415097824__actiinen7-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIINEN7 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d94483e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d94483e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d94483e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d94483e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="lsh1733415097824__31-4-reset-2" rowspan="1">
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
    INEN3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input trigger &lt;n&gt; to output channel &lt;x&gt; enable.
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
       Input trigger &lt;n&gt; will not generate an event on output channel &lt;x&gt;.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Input trigger &lt;n&gt; will generate an event on output channel &lt;x&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsh1733415097824__id-3-reset-2" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INEN2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input trigger &lt;n&gt; to output channel &lt;x&gt; enable.
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
       Input trigger &lt;n&gt; will not generate an event on output channel &lt;x&gt;.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Input trigger &lt;n&gt; will generate an event on output channel &lt;x&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsh1733415097824__id-2-reset-2" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INEN1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input trigger &lt;n&gt; to output channel &lt;x&gt; enable.
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
       Input trigger &lt;n&gt; will not generate an event on output channel &lt;x&gt;.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Input trigger &lt;n&gt; will generate an event on output channel &lt;x&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsh1733415097824__id-1-reset-2" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    INEN0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Input trigger &lt;n&gt; to output channel &lt;x&gt; enable.
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
       Input trigger &lt;n&gt; will not generate an event on output channel &lt;x&gt;.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Input trigger &lt;n&gt; will generate an event on output channel &lt;x&gt;.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="lsh1733415097824__id-0-reset-2" rowspan="1">
    <span>
     x
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
   <th class="documents-nocellnorowborder" colspan="1" id="d94483e352" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d94483e355" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d94483e358" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d94483e361" rowspan="1">
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
    0x3C
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIINEN7
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
