# DBROM_CIDR2, DebugBlock ROM table Component Identification Register 2

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-Debug-APB-bus/External-debug-ROM-registers-summary/DBROM-CIDR2--DebugBlock-ROM-table-Component-Identification-Register-2>

### DBROM\_CIDR2, DebugBlock ROM table Component Identification Register 2

Provides CoreSight discovery information.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   DBROM

Register offset
:   0xFF8

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0000 0101
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_dbrom\_cidr2 bit assignments

![ext_dbrom_cidr2 bit assignments](images/0577-DBROM_CIDR2-DebugBlock-ROM-table-Component-Identification-Register-2-img01.svg)

<table id="lpv1733415282412__adbrom_cidr2-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DBROM_CIDR2 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d166385e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d166385e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d166385e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d166385e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="lpv1733415282412__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PRMBL_2
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CoreSight component identification preamble.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000101
      </span>
     </dt>
     <dd>
      <p>
       CoreSight component identification preamble.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="lpv1733415282412__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x05
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
