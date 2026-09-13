# CTIOUTEN7, CTI Input Channel to Output Trigger Enable registers

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIOUTEN7--CTI-Input-Channel-to-Output-Trigger-Enable-registers>

### CTIOUTEN7, CTI Input Channel to Output Trigger Enable registers

Defines which input channels generate output trigger n.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0xBC

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

Figure 1. ext\_ctiouten7 bit assignments

![ext_ctiouten7 bit assignments](images/0459-CTIOUTEN7-CTI-Input-Channel-to-Output-Trigger-Enable-registers-img01.svg)

<table id="viw1733415110056__actiouten7-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIOUTEN7 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d32334e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d32334e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d32334e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d32334e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="viw1733415110056__31-4-reset-2" rowspan="1">
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
    OUTEN3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input channel &lt;x&gt; to output trigger &lt;n&gt; enable.
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
       An event on input channel &lt;x&gt; will not cause output trigger &lt;n&gt; to be asserted.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An event on input channel &lt;x&gt; will cause output trigger &lt;n&gt; to be asserted.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="viw1733415110056__id-3-reset-2" rowspan="1">
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
    OUTEN2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input channel &lt;x&gt; to output trigger &lt;n&gt; enable.
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
       An event on input channel &lt;x&gt; will not cause output trigger &lt;n&gt; to be asserted.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An event on input channel &lt;x&gt; will cause output trigger &lt;n&gt; to be asserted.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="viw1733415110056__id-2-reset-2" rowspan="1">
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
    OUTEN1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Input channel &lt;x&gt; to output trigger &lt;n&gt; enable.
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
       An event on input channel &lt;x&gt; will not cause output trigger &lt;n&gt; to be asserted.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An event on input channel &lt;x&gt; will cause output trigger &lt;n&gt; to be asserted.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="viw1733415110056__id-1-reset-2" rowspan="1">
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
    OUTEN0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Input channel &lt;x&gt; to output trigger &lt;n&gt; enable.
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
       An event on input channel &lt;x&gt; will not cause output trigger &lt;n&gt; to be asserted.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An event on input channel &lt;x&gt; will cause output trigger &lt;n&gt; to be asserted.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="viw1733415110056__id-0-reset-2" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d32334e352" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d32334e355" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d32334e358" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d32334e361" rowspan="1">
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
    0xBC
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIOUTEN7
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
