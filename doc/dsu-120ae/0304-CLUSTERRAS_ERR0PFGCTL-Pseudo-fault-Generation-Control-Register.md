# CLUSTERRAS_ERR0PFGCTL, Pseudo-fault Generation Control Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0PFGCTL--Pseudo-fault-Generation-Control-Register>

### CLUSTERRAS\_ERR0PFGCTL, Pseudo-fault Generation Control Register

Enables controlled fault generation.

### Configurations

External register CLUSTERRAS\_ERR0PFGCTL bits [63:0] are architecturally mapped to AArch64 System register [ERXPFGCTL\_EL1, Selected Pseudo-fault Generation Control Register](/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXPFGCTL-EL1--Selected-Pseudo-fault-Generation-Control-Register?lang=en "Accesses the ext-CLUSTERRAS_ERR0PFGCTL register when the value in AArch64-ERRSELR_EL1.SEL is set to 0.") bits [63:0].

### Attributes

Width
:   64

Component
:   CLUSTERRAS

Register offset
:   0x808

Access type
:   See bit descriptions

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx 0xxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_err0pfgctl bit assignments

![ext_clusterras_err0pfgctl bit assignments](images/0304-CLUSTERRAS_ERR0PFGCTL-Pseudo-fault-Generation-Control-Register-img01.svg)

<table id="lhi1733414909190__aclusterras_err0pfgctl-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERR0PFGCTL bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d240430e151" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d240430e154" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d240430e157" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d240430e160" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [63:32]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__63-32-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CDNEN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Countdown Enable. Controls transfers from the value that is held in the ext-CLUSTERRAS_ERR0PFGCDN into the Error Generation Counter, and enables this counter.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       The Error Generation Counter is disabled.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The Error Generation Counter is enabled. On a write of 1 to this bit, the Error Generation Counter is set to ext-CLUSTERRAS_ERR0PFGCDN.CDN.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-31-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    R
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Restart. Controls whether, on reaching zero, the Error Generation Counter restarts from the ext-CLUSTERRAS_ERR0PFGCDN value, or stops.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       On reaching 0, the Error Generation Counter stops.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       On reaching 0, the Error Generation Counter is set to ext-CLUSTERRAS_ERR0PFGCDN.CDN.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-30-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [29:13]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__29-13-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MV
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Miscellaneous syndrome. The value that is written to ext-CLUSTERRAS_ERR0STATUS.MV when an injected error is recorded.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.MV is set to 0 when an injected error is recorded.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.MV is set to 1 when an injected error is recorded.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-12-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    AV
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Address syndrome. The value that is written to ext-CLUSTERRAS_ERR0STATUS.AV when an injected error is recorded.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.AV is set to 0 when an injected error is recorded.
      </p>
     </dd>
    </dl>
    <p>
     This bit is
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     Access to this field is:
     <span class="documents-archterm">
      RES0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-11-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Poison flag. The value that is written to ext-CLUSTERRAS_ERR0STATUS.PN when an injected error is recorded.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.PN is set to 0 when an injected error is recorded.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.PN is set to 1 when an injected error is recorded.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-10-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ER
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Error Reported flag. The value that is written to ext-CLUSTERRAS_ERR0STATUS.ER when an injected error is recorded.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.ER is set to 0 when an injected error is recorded.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.ER is set to 1 when an injected error is recorded.
      </p>
     </dd>
    </dl>
    <p>
     This bit is
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     Access to this field is:
     <span class="documents-archterm">
      RES0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-9-reset" rowspan="1">
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
    CI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Critical Error flag. The value that is written to ext-CLUSTERRAS_ERR0STATUS.CI when an injected error is recorded.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.CI is set to 0 when an injected error is recorded.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.CI is set to 1 when an injected error is recorded.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-8-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Corrected Error generation enable. Controls the type of Corrected Error condition that might be generated.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       No error of this type is generated.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       A non-specific Corrected Error, that is, a Corrected Error that is recorded as ext-CLUSTERRAS_ERR0STATUS.CE == 0b10, might be generated when the Error Generation Counter decrements to zero.
      </p>
     </dd>
    </dl>
    <p>
     The set of permitted values for this field is defined by ext-CLUSTERRAS_ERR0PFGF.CE.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-7-6-reset" rowspan="1">
    <span>
     xx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Deferred Error generation enable. Controls whether this type of error condition might be generated.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error of this type is generated.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An error of this type might be generated when the Error Generation Counter decrements to zero.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-5-reset" rowspan="1">
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
    UEO
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Latent or Restartable Error generation enable. Controls whether this type of error condition might be generated.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error of this type is generated.
      </p>
     </dd>
    </dl>
    <p>
     This bit is
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     Access to this field is:
     <span class="documents-archterm">
      RES0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-4-reset" rowspan="1">
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
    UER
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Signaled or Recoverable Error generation enable. Controls whether this type of error condition might be generated.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error of this type is generated.
      </p>
     </dd>
    </dl>
    <p>
     This bit is
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     Access to this field is:
     <span class="documents-archterm">
      RES0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-3-reset" rowspan="1">
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
    UEU
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Unrecoverable Error generation enable. Controls whether this type of error condition might be generated.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error of this type is generated.
      </p>
     </dd>
    </dl>
    <p>
     This bit is
     <span class="documents-archterm">
      RES0
     </span>
     .
    </p>
    <p>
     Access to this field is:
     <span class="documents-archterm">
      RES0
     </span>
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-2-reset" rowspan="1">
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
    UC
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncontainable Error generation enable. Controls whether this type of error condition might be generated.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No error of this type is generated.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An error of this type might be generated when the Error Generation Counter decrements to zero.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lhi1733414909190__id-1-reset" rowspan="1">
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
    OF
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Overflow flag. The value that is written to ext-CLUSTERRAS_ERR0STATUS.OF when an injected error is recorded.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.OF is set to 0 when an injected error is recorded.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0STATUS.OF is set to 1 when an injected error is recorded.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="lhi1733414909190__id-0-reset" rowspan="1">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d240430e991" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d240430e994" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d240430e997" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d240430e1000" rowspan="1">
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
    0x808
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERR0PFGCTL
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
