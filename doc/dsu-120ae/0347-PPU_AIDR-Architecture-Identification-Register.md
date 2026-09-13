# PPU_AIDR, Architecture Identification Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-PPU-registers-summary/PPU-AIDR--Architecture-Identification-Register>

### PPU\_AIDR, Architecture Identification Register

This register identifies the PPU architecture revision.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   PPU

Register offset
:   0xFCC

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx xxxx 0001 0010
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ppu\_aidr bit assignments

![ext_ppu_aidr bit assignments](images/0347-PPU_AIDR-Architecture-Identification-Register-img01.svg)

<table id="hms1733414991176__appu_aidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU_AIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d228823e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d228823e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d228823e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d228823e150" rowspan="1">
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
   <td class="documents-cell-norowborder" colspan="1" id="hms1733414991176__31-8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7:4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    ARCH_REV_MAJOR
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     PPU architecture major revision.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       PPU architecture major revision 1.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="hms1733414991176__id-7-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0001
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [3:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    ARCH_REV_MINOR
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     PPU architecture minor revision.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0010
      </span>
     </dt>
     <dd>
      <p>
       PPU architecture minor revision 2.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="hms1733414991176__id-3-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0010
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
