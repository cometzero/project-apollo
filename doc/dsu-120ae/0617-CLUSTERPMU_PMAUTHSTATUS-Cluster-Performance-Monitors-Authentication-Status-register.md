# CLUSTERPMU_PMAUTHSTATUS, Cluster Performance Monitors Authentication Status register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-PMU-registers-summary/CLUSTERPMU-PMAUTHSTATUS--Cluster-Performance-Monitors-Authentication-Status-register>

### CLUSTERPMU\_PMAUTHSTATUS, Cluster Performance Monitors Authentication Status register

Provides information about the state of the authentication interface for Performance Monitors.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERPMU

Register offset
:   0xFB8

Access type
:   See bit descriptions

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_clusterpmu\_pmauthstatus bit assignments

![ext_clusterpmu_pmauthstatus bit assignments](images/0617-CLUSTERPMU_PMAUTHSTATUS-Cluster-Performance-Monitors-Authentication-Status-register-img01.svg)

<table id="sls1733415333545__aclusterpmu_pmauthstatus-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERPMU_PMAUTHSTATUS bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d161409e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d161409e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d161409e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d161409e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="sls1733415333545__31-8-reset" rowspan="1">
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
    <p>
     ExternalSecureNoninvasiveDebugEnabled() == ExternalSecureInvasiveDebugEnabled().
    </p>
    <p>
     This field has the same value as the SID field.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sls1733415333545__id-7-6-reset" rowspan="1">
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
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Secure invasive debug disabled. ExternalSecureInvasiveDebugEnabled() == FALSE.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Secure invasive debug enabled. ExternalSecureInvasiveDebugEnabled() == TRUE.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="sls1733415333545__id-5-4-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="sls1733415333545__id-3-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
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
   <td class="documents-cellrowborder" colspan="1" id="sls1733415333545__id-1-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

When IsCorePowered()
:   RO

Otherwise
:   ERROR
