# PPU_IIDR, Implementation Identification Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-IIDR--Implementation-Identification-Register>

### PPU\_IIDR, Implementation Identification Register

This register provides information about the implementer and implementation of the PPU.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   PPU

Register offset
:   0xFC8

Access type
:   RO

Reset value
:   0000 1011 0110 0010 0000 0100 0011 1011

### Bit descriptions

Figure 1. ext\_ppu\_iidr bit assignments

![ext_ppu_iidr bit assignments](images/0421-PPU_IIDR-Implementation-Identification-Register-img01.svg)

<table id="nkz1733415068331__appu_iidr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU_IIDR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d231875e137" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d231875e140" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d231875e143" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d231875e146" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:20]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PRODUCT_ID
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Value identifying the PPU part.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b000010110110
      </span>
     </dt>
     <dd>
      <p>
       Power Policy Unit.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nkz1733415068331__id-31-20-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x0B6
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [19:16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    VARIANT
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Value used to distinguish PPU variants, or major revisions of the PPU.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       PPU variant 0.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       PPU variant 1.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0010
      </span>
     </dt>
     <dd>
      <p>
       PPU variant 2.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0011
      </span>
     </dt>
     <dd>
      <p>
       PPU variant 3.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       PPU variant 4.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nkz1733415068331__id-19-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0010
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15:12]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    REVISION
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Value used to distinguish minor revisions of the PPU.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       PPU revision 0.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       PPU revision 1.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0010
      </span>
     </dt>
     <dd>
      <p>
       PPU revision 2.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0011
      </span>
     </dt>
     <dd>
      <p>
       PPU revision 3.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       PPU revision 4.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="nkz1733415068331__id-15-12-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [11:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    IMPLEMENTER
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Implementer identification.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b010000111011
      </span>
     </dt>
     <dd>
      <p>
       Arm Limited.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="nkz1733415068331__id-11-0-reset" rowspan="1">
    <span class="documents-g.number.hex">
     0x43B
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
