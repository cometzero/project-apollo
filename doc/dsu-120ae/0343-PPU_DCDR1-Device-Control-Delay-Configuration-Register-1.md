# PPU_DCDR1, Device Control Delay Configuration Register 1

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-PPU-registers-summary/PPU-DCDR1--Device-Control-Delay-Configuration-Register-1>

### PPU\_DCDR1, Device Control Delay Configuration Register 1

This register is used to program device control delay parameters.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   PPU

Register offset
:   0x174

Access type
:   RW

Reset value
:   ```
    xxxx xxxx xxxx xxxx 0000 0000 0000 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ppu\_dcdr1 bit assignments

![ext_ppu_dcdr1 bit assignments](images/0343-PPU_DCDR1-Device-Control-Delay-Configuration-Register-1-img01.svg)

<table id="iyy1733414985551__appu_dcdr1-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU_DCDR1 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d245963e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d245963e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d245963e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d245963e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="iyy1733414985551__31-16-reset" rowspan="1">
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
    CLKEN_ISO_DLY
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Delay in PPUCLK clock cycles from clock enable de-assertion to isolation enable assertion.Delay calculated as CLKEN_ISO_DLY + 1. Valid values for the field are in the range 0-255.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="iyy1733414985551__id-15-8-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [7:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ISO_RST_DLY
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Delay in PPUCLK clock cycles from isolation enable assertion to reset assertion.Delay calculated as ISO_RST_DLY + 1. Valid values for the field are in the range 0-255.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="iyy1733414985551__id-7-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RW
