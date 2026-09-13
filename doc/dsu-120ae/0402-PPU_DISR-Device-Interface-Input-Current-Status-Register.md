# PPU_DISR, Device Interface Input Current Status Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-DISR--Device-Interface-Input-Current-Status-Register>

### PPU\_DISR, Device Interface Input Current Status Register

This read-only register contains status reflecting the values of the device interface inputs.

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   PPU

Register offset
:   0x010

Access type
:   RO

Reset value
:   ```
    xxxx xxxx xxxx xxxx xxxx x000 0000 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ppu\_disr bit assignments

![ext_ppu_disr bit assignments](images/0402-PPU_DISR-Device-Interface-Input-Current-Status-Register-img01.svg)

<table id="azz1733415045906__appu_disr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU_DISR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d237742e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d237742e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d237742e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d237742e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:11]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="azz1733415045906__31-11-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [10:0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    PWR_DEVACTIVE_STATUS
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Status of the power mode DEVPACTIVE inputs.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b00000000000
      </span>
     </dt>
     <dd>
      <p>
       Minimum mode OFF.
      </p>
     </dd>
     <dt class="documents-dlterm">
      0000000001x
     </dt>
     <dd>
      <p>
       Minimum mode OFF_EMU.
      </p>
     </dd>
     <dt class="documents-dlterm">
      000001xxxxx
     </dt>
     <dd>
      <p>
       Minimum mode FULL_RET.
      </p>
     </dd>
     <dt class="documents-dlterm">
      0001xxxxxxx
     </dt>
     <dd>
      <p>
       Minimum mode FUNC_RET.
      </p>
     </dd>
     <dt class="documents-dlterm">
      001xxxxxxxx
     </dt>
     <dd>
      <p>
       Minimum mode ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      01xxxxxxxxx
     </dt>
     <dd>
      <p>
       Minimum mode WARM_RST.
      </p>
     </dd>
     <dt class="documents-dlterm">
      1xxxxxxxxxx
     </dt>
     <dd>
      <p>
       Minimum mode DBG_RECOV.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="azz1733415045906__id-10-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b00000000000
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RO
