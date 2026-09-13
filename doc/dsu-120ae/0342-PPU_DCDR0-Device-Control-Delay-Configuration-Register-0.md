# PPU_DCDR0, Device Control Delay Configuration Register 0

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-PPU-registers-summary/PPU-DCDR0--Device-Control-Delay-Configuration-Register-0>

### PPU\_DCDR0, Device Control Delay Configuration Register 0

This register is used to program device control delay parameters.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   PPU

Register offset
:   0x170

Access type
:   RW

Reset value
:   ```
    xxxx xxxx 0000 0000 0000 0000 0000 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ppu\_dcdr0 bit assignments

![ext_ppu_dcdr0 bit assignments](images/0342-PPU_DCDR0-Device-Control-Delay-Configuration-Register-0-img01.svg)

<table id="wgw1733414984766__appu_dcdr0-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU_DCDR0 bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d164017e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d164017e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d164017e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d164017e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wgw1733414984766__31-24-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    RST_HWSTAT_DLY
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Delay in PPUCLK clock cycles from reset de-assertion to HWSTAT update.Delay calculated as RST_HWSTAT_DLY + 1. Valid values for the field are in the range 0-255.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wgw1733414984766__id-23-16-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x00
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ISO_CLKEN_DLY
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Delay in PPUCLK clock cycles from isolation enable de-assertion to clock enable assertion.Delay calculated as ISO_CLKEN_DLY + 1. Valid values for the field are in the range 0-255.
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="wgw1733414984766__id-15-8-reset" rowspan="1">
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
    CLKEN_RST_DLY
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Delay in PPUCLK clock cycles from clock enable assertion to reset de-assertion.Delay calculated as CLKEN_RST_DLY + 1. Valid values for the field are in the range 0-255.
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="wgw1733414984766__id-7-0-reset" rowspan="1">
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
