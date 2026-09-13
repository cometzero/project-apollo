# CLUSTERROM_DBGPCR11, Cluster ROM table Debug Power Control Register 11

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary/CLUSTERROM-DBGPCR11--Cluster-ROM-table-Debug-Power-Control-Register-11>

### CLUSTERROM\_DBGPCR11, Cluster ROM table Debug Power Control Register 11

Controls power requests for PDCOMPLEX11.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERROM

Register offset
:   0xA2C

Access type
:   RO

### Bit descriptions

When NUM\_CORES >= 12

Figure 1. ext\_clusterrom\_dbgpcr11 bit assignments

![ext_clusterrom_dbgpcr11 bit assignments](images/0515-CLUSTERROM_DBGPCR11-Cluster-ROM-table-Debug-Power-Control-Register-11-img01.svg)

<table id="lqq1733415191350__aclusterrom_dbgpcr11-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERROM_DBGPCR11 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d105332e132" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d105332e135" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d105332e138" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d105332e141" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lqq1733415191350__31-2-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Power Request.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       Power is not requested for target core or complex power domain.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Power is requested for target core or complex power domain.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lqq1733415191350__id-1-reset" rowspan="1">
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
    PRESENT
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Power request implemented.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Power request for target core or complex power domain is included in the PPU power control.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="lqq1733415191350__id-0-reset" rowspan="1">
    <span>
     x
    </span>
   </td>
  </tr>
 </tbody>
</table>

When NUM\_CORES < 12

Figure 2. ext\_clusterrom\_dbgpcr11 bit assignments

![ext_clusterrom_dbgpcr11 bit assignments](images/0515-CLUSTERROM_DBGPCR11-Cluster-ROM-table-Debug-Power-Control-Register-11-img02.svg)

<table id="lqq1733415191350__aclusterrom_dbgpcr11-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   CLUSTERROM_DBGPCR11 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d105332e301" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d105332e304" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d105332e307" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d105332e310" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [31:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cellrowborder" colspan="1" id="lqq1733415191350__31-0-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RW
