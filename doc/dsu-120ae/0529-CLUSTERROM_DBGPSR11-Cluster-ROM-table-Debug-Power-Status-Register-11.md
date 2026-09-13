# CLUSTERROM_DBGPSR11, Cluster ROM table Debug Power Status Register 11

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-cluster-ROM-registers-summary/CLUSTERROM-DBGPSR11--Cluster-ROM-table-Debug-Power-Status-Register-11>

### CLUSTERROM\_DBGPSR11, Cluster ROM table Debug Power Status Register 11

Indicates the power status for PDCOMPLEX11.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   CLUSTERROM

Register offset
:   0xAAC

Access type
:   RO

### Bit descriptions

When NUM\_CORES >= 12

Figure 1. ext\_clusterrom\_dbgpsr11 bit assignments

![ext_clusterrom_dbgpsr11 bit assignments](images/0529-CLUSTERROM_DBGPSR11-Cluster-ROM-table-Debug-Power-Status-Register-11-img01.svg)

<table id="jjk1733415215531__aclusterrom_dbgpsr11-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CLUSTERROM_DBGPSR11 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d216504e132" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d216504e135" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d216504e138" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d216504e141" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="jjk1733415215531__31-2-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [1:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Power Status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00
      </span>
     </dt>
     <dd>
      <p>
       Target core or complex debug power domain might not be powered.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b01
      </span>
     </dt>
     <dd>
      <p>
       Target core or complex debug power domain is powered.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b10
      </span>
     </dt>
     <dd>
      <p>
       Reserved.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       Target core or complex debug power domain is powered and must remain powered until DBGPCR0.PR is set to 0.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="jjk1733415215531__id-1-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00
    </span>
   </td>
  </tr>
 </tbody>
</table>

When NUM\_CORES < 12

Figure 2. ext\_clusterrom\_dbgpsr11 bit assignments

![ext_clusterrom_dbgpsr11 bit assignments](images/0529-CLUSTERROM_DBGPSR11-Cluster-ROM-table-Debug-Power-Status-Register-11-img02.svg)

<table id="jjk1733415215531__aclusterrom_dbgpsr11-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   CLUSTERROM_DBGPSR11 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d216504e292" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d216504e295" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d216504e298" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d216504e301" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="jjk1733415215531__31-0-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
