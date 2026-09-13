# PPU_MEMRR, Memory Retention RAM Configuration Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-PPU-registers-summary/PPU-MEMRR--Memory-Retention-RAM-Configuration-Register>

### PPU\_MEMRR, Memory Retention RAM Configuration Register

This register is reserved.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   PPU

Register offset
:   0x058

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

Figure 1. ext\_ppu\_memrr bit assignments

![ext_ppu_memrr bit assignments](images/0341-PPU_MEMRR-Memory-Retention-RAM-Configuration-Register-img01.svg)

<table id="hgf1733414983787__appu_memrr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU_MEMRR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d16501e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16501e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d16501e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d16501e150" rowspan="1">
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
   <td class="documents-cellrowborder" colspan="1" id="hgf1733414983787__31-0-reset" rowspan="1">
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
