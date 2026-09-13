# CLUSTERRAS_ERR0CTLR, Error Record Control Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0CTLR--Error-Record-Control-Register>

### CLUSTERRAS\_ERR0CTLR, Error Record Control Register

The error control register contains enable bits for the node that writes to this record, which:

- Enable error detection and correction.
- Enable an error recovery interrupt.
- Enable a fault handling interrupt.
- Enable error recovery reporting as a read or write error response.
- Enable a critical error interrupt.

### Configurations

External register CLUSTERRAS\_ERR0CTLR bits [63:0] are architecturally mapped to AArch64 System register [ERXCTLR\_EL1, Selected Error Record Control Register](/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXCTLR-EL1--Selected-Error-Record-Control-Register?lang=en "Accesses ext-CLUSTERRAS_ERR0CTLR when the value in AArch64-ERRSELR_EL1.SEL is set to 0.") bits [63:0].

### Attributes

Width
:   64

Component
:   CLUSTERRAS

Register offset
:   0x008

Access type
:   See bit descriptions

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx xx0x x0x0 xxx0 0001
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_err0ctlr bit assignments

![ext_clusterras_err0ctlr bit assignments](images/0296-CLUSTERRAS_ERR0CTLR-Error-Record-Control-Register-img01.svg)

<table id="wat1733414900205__aclusterras_err0ctlr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERR0CTLR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d47556e190" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d47556e193" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d47556e196" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d47556e199" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:14]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__63-14-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [13]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Critical error interrupt enable.
    </p>
    <p>
     When enabled, the critical error interrupt is generated for a critical error condition.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Critical error interrupt not generated for critical errors. Critical errors are treated as Uncontained errors.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Critical error interrupt generated for critical errors.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__id-13-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [12:11]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__12-11-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DUI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Error recovery interrupt for deferred errors enable. This control applies to errors arising from both reads and writes.
    </p>
    <p>
     When enabled, an error recovery interrupt is generated for all detected Deferred errors.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Error recovery interrupt not generated for deferred errors.
      </p>
     </dd>
    </dl>
    <p>
     The interrupt is generated even if the error syndrome is discarded because the error record already records a higher priority error.
    </p>
    <p>
     Access to this field is: RO
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__id-10-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__9-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CFI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fault handling interrupt for Corrected errors enable. This control applies to errors arising from both reads and writes.
    </p>
    <p>
     When enabled, the fault handling interrupt is generated when a Corrected error counter overflows and the overflow bit for the counter is set to 1. For more information, see ext-ERR&lt;n&gt;MISC0.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Fault handling interrupt not generated for Corrected errors.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Fault handling interrupt generated for Corrected errors.
      </p>
     </dd>
    </dl>
    <p>
     The interrupt is generated even if the error syndrome is discarded because the error record already records a higher priority error.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__id-8-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
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
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__7-5-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__4-reset" rowspan="1">
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
    FI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Fault handling interrupt enable. This control applies to errors arising from both reads and writes.
    </p>
    <p>
     When enabled, the fault handling interrupt is generated for all detected Corrected errors, Deferred errors, and Uncorrected errors.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Fault handling interrupt disabled.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Fault handling interrupt enabled.
      </p>
     </dd>
    </dl>
    <p>
     The interrupt is generated even if the error syndrome is discarded because the error record already records a higher priority error.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__id-3-reset" rowspan="1">
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
    UI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncorrected error recovery interrupt enable. This control applies to errors arising from both reads and writes.
    </p>
    <p>
     When enabled, the error recovery interrupt is generated for all detected Uncorrected errors that are not deferred.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Error recovery interrupt disabled.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Error recovery interrupt enabled.
      </p>
     </dd>
    </dl>
    <p>
     The interrupt is generated even if the error syndrome is discarded because the error record already records a higher priority error.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__id-2-reset" rowspan="1">
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
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wat1733414900205__1-reset" rowspan="1">
    <span class="documents-archterm">
     RAZ/WI
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ED
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Error reporting and logging enable.
    </p>
    <p>
     When disabled, the node behaves as if error detection and correction are disabled, and no errors are recorded or signaled by the node.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Error reporting disabled.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Error reporting enabled.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="wat1733414900205__id-0-reset" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d47556e585" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d47556e588" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d47556e591" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d47556e594" rowspan="1">
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
    0x008
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERR0CTLR
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
