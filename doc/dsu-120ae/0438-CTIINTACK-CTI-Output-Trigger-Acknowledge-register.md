# CTIINTACK, CTI Output Trigger Acknowledge register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-and-core-CTI-registers-summary/CTIINTACK--CTI-Output-Trigger-Acknowledge-register>

### CTIINTACK, CTI Output Trigger Acknowledge register

Can be used to deactivate the output triggers.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CTI

Register offset
:   0x010

Access type
:   See bit descriptions

Reset value
:   ```
    0000 0000 0000 0000 0000 00xx xxxx xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ctiintack bit assignments

![ext_ctiintack bit assignments](images/0438-CTIINTACK-CTI-Output-Trigger-Acknowledge-register-img01.svg)

<table id="jiw1733415083187__actiintack-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CTIINTACK bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d8524e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d8524e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d8524e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d8524e150" rowspan="1">
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
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__31-10-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACK9
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-9-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACK8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-8-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACK7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-7-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACK6
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-6-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACK5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-5-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACK4
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-4-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ACK3
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-3-reset" rowspan="1">
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
    ACK2
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-2-reset" rowspan="1">
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
    ACK1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jiw1733415083187__id-1-reset" rowspan="1">
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
    ACK0
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Acknowledge for output trigger &lt;n&gt;.
    </p>
    <p>
     If any of the following is true, writes to ACK&lt;n&gt; are ignored:
    </p>
    <ul>
     <li>
      n &gt;= ext-CTIDEVID.NUMTRIG, the number of implemented triggers.
     </li>
     <li>
      Output trigger n is not active.
     </li>
     <li>
      The channel mapping function output, as controlled by ext-CTIOUTEN&lt;n&gt;, is still active.
     </li>
     <li>
      Output trigger n is not implemented.
     </li>
     <li>
      Output trigger n is not connected.
     </li>
     <li>
      Output trigger n is self-acknowledging and does not require software acknowledge.
     </li>
    </ul>
    <p>
     Otherwise, the behavior on writes to ACK&lt;n&gt; is as follows:
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No effect
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Deactivate the trigger.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="jiw1733415083187__id-0-reset" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d8524e825" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d8524e828" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d8524e831" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d8524e834" rowspan="1">
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
    0x010
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CTIINTACK
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

When SoftwareLockStatus()
:   WI

When !SoftwareLockStatus()
:   WO
