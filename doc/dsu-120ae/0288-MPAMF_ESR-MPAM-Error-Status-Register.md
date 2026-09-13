# MPAMF_ESR, MPAM Error Status Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-MPAM-registers-summary/MPAMF-ESR--MPAM-Error-Status-Register>

### MPAMF\_ESR, MPAM Error Status Register

Indicates MPAM error status for this MSC. MPAMF\_ESR\_s reports Secure MPAM errors. MPAMF\_ESR\_ns reports Non-secure MPAM errors.

Software should write this register after reading the status of an error to reset ERRCODE to 0x0000 and OVRWR to 0 so that future errors are not reported with OVRWR set.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   MPAM

Register offsets (2)
:   0x00F8,0x00F8

Access type
:   RW

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_mpamf\_esr bit assignments

![ext_mpamf_esr bit assignments](images/0288-MPAMF_ESR-MPAM-Error-Status-Register-img01.svg)

<table id="gjk1733414936904__ampamf_esr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   MPAMF_ESR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e147" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e150" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e153" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d53645e156" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OVRWR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Overwritten.
    </p>
    <p>
     If 0 and ERRCODE ==
     <span class="documents-g.number.bin">
      0b0000
     </span>
     , no errors have occurred.
    </p>
    <p>
     If 0 and ERRCODE is non-zero, a single error has occurred and is recorded in this register.
    </p>
    <p>
     If 1 and ERRCODE is non-zero, multiple errors have occurred and this register records the most recent error.
    </p>
    <p>
     The state where this bit is 1 and ERRCODE is 0 must not be produced by hardware and is only reached when software writes this combination into this register.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gjk1733414936904__id-31-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [30:28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gjk1733414936904__30-28-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ERRCODE
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Error code.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       No error.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       PARTID_SEL_Range.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0010
      </span>
     </dt>
     <dd>
      <p>
       Req_PARTID_Range.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0011
      </span>
     </dt>
     <dd>
      <p>
       MSMONCFG_ID_RANGE.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       Req_PMG_Range.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0101
      </span>
     </dt>
     <dd>
      <p>
       Monitor_Range.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0110
      </span>
     </dt>
     <dd>
      <p>
       intPARTID_Range.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0111
      </span>
     </dt>
     <dd>
      <p>
       Unexpected_INTERNAL.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1000
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1001
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1010
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1011
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1100
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1101
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1110
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1111
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gjk1733414936904__id-27-24-reset" rowspan="1">
    <span>
     xxxx
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PMG
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Program monitoring group.
    </p>
    <p>
     Set to the PMG on an error that captures PMG. Otherwise, set to
     <span class="documents-g.number.hex">
      0x00
     </span>
     on an error that does not capture PMG.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="gjk1733414936904__id-23-16-reset" rowspan="1">
    <code>
     8{x}
    </code>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [15:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PARTID_MON
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PARTID or monitor.
    </p>
    <p>
     Set to the PARTID on an error that captures PARTID.
    </p>
    <p>
     Set to the monitor index on an error that captures MON.
    </p>
    <p>
     On an error that captures neither PARTID nor MON, this field is set to
     <span class="documents-g.number.hex">
      0x0000
     </span>
     .
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="gjk1733414936904__id-15-0-reset" rowspan="1">
    <code>
     16{x}
    </code>
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
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e565" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e568" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e571" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d53645e574" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x00F8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_ESR_s
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW

<table>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e622" rowspan="1">
    Component
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e625" rowspan="1">
    Offset
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53645e628" rowspan="1">
    Instance
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d53645e631" rowspan="1">
    Range
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAM
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    0x00F8
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    MPAMF_ESR_ns
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    None
   </td>
  </tr>
 </tbody>
</table>

This interface is accessible as follows:

RW
