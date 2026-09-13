# DBROM_ROMENTRY1, DebugBlock ROM table Entry 1

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-debug-ROM-registers-summary/DBROM-ROMENTRY1--DebugBlock-ROM-table-Entry-1>

### DBROM\_ROMENTRY1, DebugBlock ROM table Entry 1

Provides the address offset for one CoreSight component.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   DBROM

Register offset
:   0x004

Access type
:   RO

Reset value
:   ```
    0000 0000 0000 1111 0000 xxxx xxxx x011
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_dbrom\_romentry1 bit assignments

![ext_dbrom_romentry1 bit assignments](images/0548-DBROM_ROMENTRY1-DebugBlock-ROM-table-Entry-1-img01.svg)

<table id="hoz1733415238611__adbrom_romentry1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DBROM_ROMENTRY1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d172198e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d172198e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d172198e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d172198e150" rowspan="1">
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
       0b00000000000001000000
      </span>
     </dt>
     <dd>
      <p>
       Cluster CTI at address 0x0004_0000.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hoz1733415238611__id-31-12-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00040
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
   <td class="documents-cell-norowborder" colspan="1" id="hoz1733415238611__11-3-reset" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="hoz1733415238611__id-2-reset" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="hoz1733415238611__id-1-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b11
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
