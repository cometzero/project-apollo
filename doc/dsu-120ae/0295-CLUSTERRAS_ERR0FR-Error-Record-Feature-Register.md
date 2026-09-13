# CLUSTERRAS_ERR0FR, Error Record Feature Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0FR--Error-Record-Feature-Register>

### CLUSTERRAS\_ERR0FR, Error Record Feature Register

Defines which of the common architecturally-defined features are implemented by the node and, of the implemented features, which are software programmable.

### Configurations

External register CLUSTERRAS\_ERR0FR bits [63:0] are architecturally mapped to AArch64 System register [ERXFR\_EL1, Selected Error Record Feature Register](/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXFR-EL1--Selected-Error-Record-Feature-Register?lang=en "Accesses ext-CLUSTERRAS_ERR0FR when the value in AArch64-ERRSELR_EL1.SEL is set to 0.") bits [63:0].

### Attributes

Width
:   64

Component
:   CLUSTERRAS

Register offset
:   0x000

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xx00 10xx 0000 1010 1001 1010 0110
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_err0fr bit assignments

![ext_clusterras_err0fr bit assignments](images/0295-CLUSTERRAS_ERR0FR-Error-Record-Feature-Register-img01.svg)

<table id="gld1733414896875__aclusterras_err0fr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERR0FR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d16993e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16993e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16993e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d16993e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:26]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__63-26-reset" rowspan="1">
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
    TS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Timestamp Extension. Not implemented and treated as
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       The node does not support a timestamp register.
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-25-24-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:22]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Critical error interrupt.
    </p>
    <p>
     Indicates whether the critical error interrupt and associated controls are implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Critical error interrupt is supported and it can be enabled using associated controls.
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-23-22-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [21:20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    INJ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fault Injection Extension.
    </p>
    <p>
     Indicates whether the RAS Common Fault Injection Model Extension is implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       The node does not implement the RAS Common Fault Injection Model Extension.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       The node implements the RAS Common Fault Injection Model Extension. See ext-CLUSTERRAS_ERR0PFGF for more information.
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-21-20-reset" rowspan="1">
    <span>
     xx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19:18]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CEO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Corrected Error overwrite.
    </p>
    <p>
     Indicates the behavior when a second Corrected error is detected after a first Corrected error has been recorded by an error record &lt;m&gt; owned by the node.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Counts Corrected errors. Keeps the previous error syndrome. If the counter overflows then CLUSTERRAS_ERR0STATUS.OF is set to 1.
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-19-18-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [17:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DUI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Error recovery interrupt for deferred errors.
    </p>
    <p>
     Indicates whether the node implements a control for enabling error recovery interrupts on deferred errors.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Does not support feature. ext-CLUSTERRAS_ERR0CTLR.DUI is
       <span class="documents-archterm">
        RES0
       </span>
       .
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-17-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RP
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Repeat counter.
    </p>
    <p>
     Indicates whether the node implements a repeat Corrected error counter in CLUSTERRAS_ERR0MISC0.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       A first (repeat) counter and a second (other) counter are implemented. The repeat counter is the same size as the primary error counter.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-15-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b1
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [14:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CEC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Corrected Error Counter.
    </p>
    <p>
     Indicates whether the node implements standard Corrected error counter (CE counter) mechanisms in CLUSTERRAS_ERR0MISC0.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010
      </span>
     </dt>
     <dd>
      <p>
       Implements an 8-bit Corrected error counter in CLUSTERRAS_ERR0MISC0[39:32].
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-14-12-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b010
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11:10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CFI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fault handling interrupt for corrected errors.
    </p>
    <p>
     Indicates whether the node implements a control for enabling fault handling interrupts on corrected errors.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Feature is controllable using ext-CLUSTERRAS_ERR0CTLR.CFI.
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-11-10-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    UE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     In-band uncorrected error reporting.
    </p>
    <p>
     Indicates whether the node implements in-band uncorrected error reporting (External aborts), and, if so, whether the node implements controls for enabling and disabling the reporting.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Feature always enabled. ext-CLUSTERRAS_ERR0CTLR.UE is
       <span class="documents-archterm">
        RES0
       </span>
       .
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-9-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b01
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    FI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fault handling interrupt.
    </p>
    <p>
     Indicates whether the node implements a fault handling interrupt, and, if so, whether the node implements controls for enabling and disabling the interrupt.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Feature is controllable using ext-CLUSTERRAS_ERR0CTLR.FI.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-7-6-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    UI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Error recovery interrupt for uncorrected errors.
    </p>
    <p>
     Indicates whether the node implements an error recovery interrupt, and, if so, whether the node implements controls for enabling and disabling the interrupt.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Feature is controllable using ext-CLUSTERRAS_ERR0CTLR.UI.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-5-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3:2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Deferred error enable.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Deferred errors is always enabled.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gld1733414896875__id-3-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b01
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [1:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ED
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Error reporting and logging.
    </p>
    <p>
     Indicates this is the first record owned by the cluster. The cluster implements controls for enabling and disabling error reporting and logging.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Feature is controllable using ext-CLUSTERRAS_ERR0CTLR.ED.
      </p>
     </dd>
    </dl>
    <p>
     The value
     <span class="documents-g.number.bin">
      0b11
     </span>
     is reserved.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="gld1733414896875__id-1-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b10
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
   <th class="documents-nocellnorowborder" colspan="1" id="d16993e660" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16993e663" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16993e666" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d16993e669" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    CLUSTERRAS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x000
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERR0FR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RO
