# PPU_DISR, Device Interface Input Current Status Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-cluster-PPU-registers-summary/PPU-DISR--Device-Interface-Input-Current-Status-Register>

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
    xxxx 0000 xxxx xxxx xxxx x000 0000 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ppu\_disr bit assignments

![ext_ppu_disr bit assignments](images/0327-PPU_DISR-Device-Interface-Input-Current-Status-Register-img01.svg)

<table id="xcj1733414966792__appu_disr-0">
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
   <th class="documents-nocellnorowborder" colspan="1" id="d367585e141" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d367585e144" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d367585e147" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d367585e150" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:28]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xcj1733414966792__31-28-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [27:24]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OP_DEVACTIVE_STATUS
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Status of the operating mode DEVPACTIVE inputs.
    </p>
    <p>
     All other values are reserved.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0000
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_00, ONE_SLICE_SF_ONLY_ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0001
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_01, ONE_SLICE_HALF_RAM_ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0011
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_03, ONE_SLICE_FULL_RAM_ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0100
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_04, ALL_SLICE_SF_ONLY_ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0101
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_05, ALL_SLICE_HALF_RAM_ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0111
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_07, ALL_SLICE_FULL_RAM_ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1000
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_08, HALF_SLICE_SF_ONLY_ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1001
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_09, HALF_SLICE_HALF_RAM_ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1011
      </span>
     </dt>
     <dd>
      <p>
       Request for OPMODE_0B, HALF_SLICE_FULL_RAM_ON.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xcj1733414966792__id-27-24-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0000
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [23:11]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="xcj1733414966792__23-11-reset" rowspan="1">
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
       Request for OFF.
      </p>
     </dd>
     <dt class="documents-dlterm">
      0000000001x
     </dt>
     <dd>
      <p>
       Request for OFF_EMU.
      </p>
     </dd>
     <dt class="documents-dlterm">
      000000001xx
     </dt>
     <dd>
      <p>
       Request for MEM_RET.
      </p>
     </dd>
     <dt class="documents-dlterm">
      00000001xxx
     </dt>
     <dd>
      <p>
       Request for MEM_RET_EMU.
      </p>
     </dd>
     <dt class="documents-dlterm">
      000001xxxxx
     </dt>
     <dd>
      <p>
       Request for FULL_RET.
      </p>
     </dd>
     <dt class="documents-dlterm">
      0001xxxxxxx
     </dt>
     <dd>
      <p>
       Request for FUNC_RET.
      </p>
     </dd>
     <dt class="documents-dlterm">
      001xxxxxxxx
     </dt>
     <dd>
      <p>
       Request for ON.
      </p>
     </dd>
     <dt class="documents-dlterm">
      01xxxxxxxxx
     </dt>
     <dd>
      <p>
       Request for WARM_RST.
      </p>
     </dd>
     <dt class="documents-dlterm">
      1xxxxxxxxxx
     </dt>
     <dd>
      <p>
       Request for DBG_RECOV.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="xcj1733414966792__id-10-0-reset" rowspan="1">
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
