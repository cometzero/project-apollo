# DBROM_ROMENTRY10, DebugBlock ROM table Entry 10

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-debug-ROM-registers-summary/DBROM-ROMENTRY10--DebugBlock-ROM-table-Entry-10>

### DBROM\_ROMENTRY10, DebugBlock ROM table Entry 10

Provides the address offset for one CoreSight component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   DBROM

Register offset
:   0x028

Access type
:   RO

### Bit descriptions

When NUM\_CORES >= 9

Figure 1. ext\_dbrom\_romentry10 bit assignments

![ext_dbrom_romentry10 bit assignments](images/0557-DBROM_ROMENTRY10-DebugBlock-ROM-table-Entry-10-img01.svg)

<table id="ndm1733415255103__adbrom_romentry10-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DBROM_ROMENTRY10 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d162363e132" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d162363e135" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d162363e138" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d162363e141" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OFFSET
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     The component address, relative to the base address of this ROM Table. The component address is calculated using the following equation:
    </p>
    <p>
     Component Address = ROM Table Base Address + (OFFSET &lt;&lt; 12).
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000010011110000
      </span>
     </dt>
     <dd>
      <p>
       Core 8 CTI at address 0x4F_0000.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ndm1733415255103__id-31-12-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x004F0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [11:3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ndm1733415255103__11-3-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    POWERIDVALID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if the Power domain ID field contains a Power domain ID.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       A power domain ID is not provided.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="ndm1733415255103__id-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [1:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PRESENT
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Indicates whether an entry is present at this location in the ROM Table.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b11
      </span>
     </dt>
     <dd>
      <p>
       The ROM Entry is present.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="ndm1733415255103__id-1-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
  </tr>
 </tbody>
</table>

When NUM\_CORES < 9

Figure 2. ext\_dbrom\_romentry10 bit assignments

![ext_dbrom_romentry10 bit assignments](images/0557-DBROM_ROMENTRY10-DebugBlock-ROM-table-Entry-10-img02.svg)

<table id="ndm1733415255103__adbrom_romentry10-1">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   DBROM_ROMENTRY10 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d162363e316" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d162363e319" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d162363e322" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d162363e325" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="ndm1733415255103__31-0-reset" rowspan="1">
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
