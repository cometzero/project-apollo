# CLUSTERRAS_ERR0STATUS, Error Record Primary Status Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-RAS-registers-summary/CLUSTERRAS-ERR0STATUS--Error-Record-Primary-Status-Register>

### CLUSTERRAS\_ERR0STATUS, Error Record Primary Status Register

Contains status information for the error record, including:

- Whether any error has been detected (valid).
- Whether any detected error was not corrected, and returned to a requester.
- Whether any detected error was not corrected and deferred.
- Whether an error record has been discarded because additional errors have been detected before the first error was handled by software (overflow).
- Whether any error has been reported.
- Whether the other error record registers contain valid information.
- Whether the error was recorded because poison data was detected or because a corrupt value was detected by an error detection code.
- A Primary error code.
- An IMPLEMENTATION DEFINED Extended error code.

Within this register:

- The {AV, V, MV} bits are valid bits that define whether the error record registers are valid.
- The {UE, OF, CE, DE, UET} bits encode the type of error or errors recorded.
- The {CI, ER, PN, IERR, SERR} fields are syndrome fields.

### Configurations

External register CLUSTERRAS\_ERR0STATUS bits [63:0] are architecturally mapped to AArch64 System register [ERXSTATUS\_EL1, Selected Error Record Primary Status Register](/documentation/107721/0001/AArch64-registers/AArch64-RAS-registers-summary/ERXSTATUS-EL1--Selected-Error-Record-Primary-Status-Register?lang=en "Accesses ext-CLUSTERRAS_ERR0STATUS when the value in AArch64-ERRSELR_EL1.SEL is set to 0.") bits [63:0].

### Attributes

Width
:   64

Component
:   CLUSTERRAS

Register offset
:   0x010

Access type
:   RW

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx 0000 0000 0000 0xxx 0000 0000 0000 0000
    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |  |
    63   59   55   51   47   43   39   35   31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterras\_err0status bit assignments

![ext_clusterras_err0status bit assignments](images/0297-CLUSTERRAS_ERR0STATUS-Error-Record-Primary-Status-Register-img01.svg)

<table id="jew1733414902854__aclusterras_err0status-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERRAS_ERR0STATUS bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d226807e240" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d226807e243" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d226807e246" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d226807e249" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__63-32-reset" rowspan="1">
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
    AV
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Address Valid.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       ext-CLUSTERRAS_ERR0ADDR not valid.
      </p>
     </dd>
    </dl>
    <p>
     This bit is unimplemented and treated as
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-31-reset" rowspan="1">
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
    V
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Status Register Valid.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       CLUSTERRAS_ERR0STATUS not valid.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       CLUSTERRAS_ERR0STATUS valid. At least one error has been recorded.
      </p>
     </dd>
    </dl>
    <p>
     This bit is read/write-one-to-clear.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-30-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [29]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    UE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncorrected error.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No errors have been detected, or all detected errors have been either corrected or deferred.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       At least one detected error was not corrected and not deferred.
      </p>
     </dd>
    </dl>
    <p>
     When clearing CLUSTERRAS_ERR0STATUS.V to 0, if this bit is nonzero, then software must write one to this bit to clear this bit to zero.
    </p>
    <p>
     This bit is not valid and reads
     <span class="documents-archterm">
      UNKNOWN
     </span>
     if CLUSTERRAS_ERR0STATUS.V is set to 0.
    </p>
    <p>
     This bit is read/write-one-to-clear.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-29-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ER
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Error Reported.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No in-band error (External abort) reported.
      </p>
     </dd>
    </dl>
    <p>
     This bit is unimplemented and treated as
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-28-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OF
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Overflow.
    </p>
    <p>
     Indicates that multiple errors have been detected. This bit is set to 1 when one of the following occurs:
    </p>
    <ul>
     <li>
      <p>
       A Corrected error is counted and the counter overflows.
      </p>
     </li>
     <li>
      <p>
       CLUSTERRAS_ERR0STATUS.V was previously set to 1 and a type of error other than a Corrected error is recorded.
      </p>
     </li>
    </ul>
    <p>
     Otherwise, this bit is unchanged when an error is recorded.
    </p>
    <p>
     A direct write that modifies the counter overflow flag indirectly might set this bit to an
     <span class="documents-archterm">
      UNKNOWN
     </span>
     value.
    </p>
    <p>
     A direct write to this bit that clears this bit to zero might indirectly set the counter overflow flag to an
     <span class="documents-archterm">
      UNKNOWN
     </span>
     value.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Since this bit was last cleared to zero, no error syndrome has been discarded and, if a Corrected error counter is implemented, it has not overflowed.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Since this bit was last cleared to zero, at least one error syndrome has been discarded or, if a Corrected error counter is implemented, it might have overflowed.
      </p>
     </dd>
    </dl>
    <p>
     If this bit is nonzero, then software must write 1 to this bit, to clear this bit to zero, when clearing CLUSTERRAS_ERR0STATUS.V to 0.
    </p>
    <p>
     This bit is not valid and reads
     <span class="documents-archterm">
      UNKNOWN
     </span>
     if CLUSTERRAS_ERR0STATUS.V is set to 0.
    </p>
    <p>
     This bit is read/write-one-to-clear.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-27-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [26]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    MV
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Miscellaneous Registers (CLUSTERRAS_ERR0MISC0) Valid.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       CLUSTERRAS_ERR0MISC0 is not valid.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       The contents of CLUSTERRAS_ERR0MISC0 contains additional information for an error recorded by this record.
      </p>
     </dd>
    </dl>
    <p>
     Only CLUSTERRAS_ERR0MISC0 is implemented. CLUSTERRAS_ERR0MISC1,2,3 are treated as
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <p>
     This bit is read/write-one-to-clear.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-26-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [25:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Corrected Error.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       No errors were corrected.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       At least one error was corrected.
      </p>
     </dd>
    </dl>
    <p>
     When clearing CLUSTERRAS_ERR0STATUS.V to 0, if this field is nonzero, then software must write ones to this field to clear this field to zero.
    </p>
    <p>
     If CLUSTERRAS_ERR0STATUS.V is set to 0, this field is not valid and reads
     <span class="documents-archterm">
      UNKNOWN
     </span>
     .
    </p>
    <p>
     This field is read/write-one-to-clear. Writing a value other than all-zeros or all-ones sets this field to an
     <span class="documents-archterm">
      UNKNOWN
     </span>
     value.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-25-24-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    DE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Deferred Error.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No errors were deferred.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       At least one error was not corrected and deferred.
      </p>
     </dd>
    </dl>
    <p>
     When clearing CLUSTERRAS_ERR0STATUS.V to 0, if this bit is nonzero, then software must write 1 to this bit to clear this bit to zero.
    </p>
    <p>
     If CLUSTERRAS_ERR0STATUS.V is set to 0, this bit is not valid and reads
     <span class="documents-archterm">
      UNKNOWN
     </span>
     .
    </p>
    <p>
     This bit is read/write-one-to-clear.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-23-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [22]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PN
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Poison.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Uncorrected error or Deferred error recorded because a corrupt value was detected.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Uncorrected error or Deferred error recorded because a poison value was detected.
      </p>
     </dd>
    </dl>
    <p>
     When clearing CLUSTERRAS_ERR0STATUS.V to 0, if this bit is nonzero, then software must write 1 to this bit to clear this bit to zero.
    </p>
    <p>
     This bit is not valid and reads
     <span class="documents-archterm">
      UNKNOWN
     </span>
     if any of the following are true:
    </p>
    <ul>
     <li>
      <p>
       CLUSTERRAS_ERR0STATUS.V is set to 0.
      </p>
     </li>
     <li>
      <p>
       CLUSTERRAS_ERR0STATUS.{DE, UE} are both set to 0.
      </p>
     </li>
    </ul>
    <p>
     This bit is read/write-one-to-clear.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-22-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [21:20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    UET
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Uncorrected Error Type.
    </p>
    <p>
     Describes the state of the component after detecting or consuming an Uncorrected error.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Uncorrected error, Uncontainable error (UC).
      </p>
     </dd>
    </dl>
    <p>
     This field is not implemented and is treated as
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-21-20-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    CI
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Critical error.
    </p>
    <p>
     Indicates whether a critical error condition has been recorded.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No critical error condition recorded.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Critical error condition recorded.
      </p>
     </dd>
    </dl>
    <p>
     When clearing CLUSTERRAS_ERR0STATUS.V to 0, if this bit is nonzero, then software must write 1 to this bit to clear this bit to zero.
    </p>
    <p>
     This bit is not valid and reads
     <span class="documents-archterm">
      UNKNOWN
     </span>
     if CLUSTERRAS_ERR0STATUS.V is set to 0.
    </p>
    <p>
     This bit is read/write-one-to-clear.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-19-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [18:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__18-16-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    IERR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-archterm">
      IMPLEMENTATION DEFINED
     </span>
     Extended error code.
    </p>
    <p>
     Used with any primary error code SERR value. Additional information is placed in the CLUSTERRAS_ERR0MISC0 register.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000
      </span>
     </dt>
     <dd>
      <p>
       If SERR == 0x7, indicates a Tag RAM error. Not used with other SERR values.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000010
      </span>
     </dt>
     <dd>
      <p>
       If SERR == 0x7, indicates a Snoop Filter RAM error. Not used with other SERR values.
      </p>
     </dd>
    </dl>
    <p>
     This field is not valid and reads
     <span class="documents-archterm">
      UNKNOWN
     </span>
     if CLUSTERRAS_ERR0STATUS.V is set to 0.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-15-8-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SERR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Primary error code.
    </p>
    <p>
     Indicates the type of Primary error.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000
      </span>
     </dt>
     <dd>
      <p>
       No error.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000001
      </span>
     </dt>
     <dd>
      <p>
       <span class="documents-archterm">
        IMPLEMENTATION DEFINED
       </span>
       error.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000010
      </span>
     </dt>
     <dd>
      <p>
       Data value from (non-associative) internal memory. For example, ECC from on-chip SRAM or buffer.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000011
      </span>
     </dt>
     <dd>
      <p>
       <span class="documents-archterm">
        IMPLEMENTATION DEFINED
       </span>
       pin. For example, nSEI pin.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000100
      </span>
     </dt>
     <dd>
      <p>
       Assertion failure. For example, consistency failure.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000101
      </span>
     </dt>
     <dd>
      <p>
       Error detected on internal data path. For example, parity on ALU result.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000110
      </span>
     </dt>
     <dd>
      <p>
       Data value from associative memory. For example, ECC error on cache data.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000111
      </span>
     </dt>
     <dd>
      <p>
       Address/control value from associative memory. For example, ECC error on cache tag.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001000
      </span>
     </dt>
     <dd>
      <p>
       Data value from a TLB. For example, ECC error on TLB data.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001001
      </span>
     </dt>
     <dd>
      <p>
       Address/control value from a TLB. For example, ECC error on TLB tag.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="jew1733414902854__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:0] continued
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SERR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001010
      </span>
     </dt>
     <dd>
      <p>
       Data value from producer. For example, parity error on write data bus.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001011
      </span>
     </dt>
     <dd>
      <p>
       Address/control value from producer. For example, parity error on address bus.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001100
      </span>
     </dt>
     <dd>
      <p>
       Data value from (non-associative) external memory. For example, ECC error in SDRAM.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001101
      </span>
     </dt>
     <dd>
      <p>
       Illegal address (software fault). For example, access to unpopulated memory.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001110
      </span>
     </dt>
     <dd>
      <p>
       Illegal access (software fault). For example, byte write to word register.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00001111
      </span>
     </dt>
     <dd>
      <p>
       Illegal state (software fault). For example, device not ready.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00010000
      </span>
     </dt>
     <dd>
      <p>
       Internal data register. For example, parity on a SIMD&amp;FP register. For a PE, all general-purpose, stack pointer, SIMD&amp;FP, and SVE registers are data registers.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00010001
      </span>
     </dt>
     <dd>
      <p>
       Internal control register. For example, Parity on a System register. For a PE, all registers other than general-purpose, stack pointer, SIMD&amp;FP, and SVE registers are control registers.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00010010
      </span>
     </dt>
     <dd>
      <p>
       Error response from subordinate. For example, error response from cache write-back.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00010011
      </span>
     </dt>
     <dd>
      <p>
       External timeout. For example, timeout on interaction with another node.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0] continued
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    SERR
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00010100
      </span>
     </dt>
     <dd>
      <p>
       Internal timeout. For example, timeout on interface within the node.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00010101
      </span>
     </dt>
     <dd>
      <p>
       Deferred error from subordinate not supported at requester. For example, poisoned data received from a subordinate by a requester that cannot defer the error further.
      </p>
     </dd>
    </dl>
    <p>
     All other values are reserved.
    </p>
    <p>
     This field is not valid and reads
     <span class="documents-archterm">
      UNKNOWN
     </span>
     if CLUSTERRAS_ERR0STATUS.V is set to 0.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
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
   <th class="documents-nocellnorowborder" colspan="1" id="d226807e1144" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d226807e1147" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d226807e1150" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d226807e1153" rowspan="1">
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
    0x010
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ERR0STATUS
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
