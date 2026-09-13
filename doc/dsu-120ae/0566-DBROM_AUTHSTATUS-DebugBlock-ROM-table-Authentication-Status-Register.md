# DBROM_AUTHSTATUS, DebugBlock ROM table Authentication Status Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-debug-ROM-registers-summary/DBROM-AUTHSTATUS--DebugBlock-ROM-table-Authentication-Status-Register>

### DBROM\_AUTHSTATUS, DebugBlock ROM table Authentication Status Register

Provides information about the state of the authentication interface for debug.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   DBROM

Register offset
:   0xFB8

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 1100
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_dbrom\_authstatus bit assignments

![ext_dbrom_authstatus bit assignments](images/0566-DBROM_AUTHSTATUS-DebugBlock-ROM-table-Authentication-Status-Register-img01.svg)

<table id="hlp1733415270349__adbrom_authstatus-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DBROM_AUTHSTATUS bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d185444e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d185444e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d185444e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d185444e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hlp1733415270349__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SNID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Secure Non-invasive Debug.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Debug level is not supported.
      </p>
     </dd>
    </dl>
    <p>
     ExternalSecureNoninvasiveDebugEnabled() == ExternalSecureInvasiveDebugEnabled().
    </p>
    <p>
     This field has the same value as the SID field.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hlp1733415270349__id-7-6-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    SID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Secure Invasive Debug.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Debug level is not supported.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hlp1733415270349__id-5-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3:2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    NSNID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Non-secure Non-invasive Debug.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Supported and enabled.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hlp1733415270349__id-3-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [1:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    NSID
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Non-secure Invasive Debug.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Debug level is not supported.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="hlp1733415270349__id-1-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
