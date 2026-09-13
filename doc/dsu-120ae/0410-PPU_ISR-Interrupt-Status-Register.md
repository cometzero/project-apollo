# PPU_ISR, Interrupt Status Register

Source: <https://developer.arm.com/documentation/107721/0001/External-registers/Registers-accessed-over-the-utility-bus/External-core-PPU-registers-summary/PPU-ISR--Interrupt-Status-Register>

### PPU\_ISR, Interrupt Status Register

This register contains information about events causing the assertion of the interrupt output. It is also used to clear interrupt events.

A bit set to 0b1 indicates the event asserted the interrupt output. Multiple events can be active at the same time. When an interrupt event is masked an occurrence of that event does not set the status bit.

A write of 0b1 to an event bit clears that event. A write of 0b0 to a bit has no effect. The interrupt output stays HIGH until all status bits in the Interrupt Status Register (PPU\_ISR) and the Additional Interrupt Status Register (PPU\_AISR) are 0b0.

When the OTHER\_IRQ bit is set, this indicates an event from the Additional Interrupt Status Register (PPU\_AISR) has caused the interrupt output to be asserted. This bit cannot be cleared by writing to this register. It must be cleared by writing to the active event in the Additional Interrupt Status Register (PPU\_AISR).

### Configurations

This register is available in all configurations.

### Attributes

Width
:   32

Component
:   PPU

Register offset
:   0x038

Access type
:   RW

Reset value
:   ```
    xxxx xxxx xxxx x000 0x0x xx0x 0x00 0000
    |    |    |    |    |    |    |    |  |
    31   27   23   19   15   11   7    3  0
    ```

    > ### Note
    >
    > Where the reset reads xxxx, see individual bits.

### Bit descriptions

Figure 1. ext\_ppu\_isr bit assignments

![ext_ppu_isr bit assignments](images/0410-PPU_ISR-Interrupt-Status-Register-img01.svg)

<table id="lsb1733415054921__appu_isr-0">
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   PPU_ISR bit descriptions
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
   <th class="documents-nocellnorowborder" colspan="1" id="d166663e154" rowspan="1">
    Bits
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d166663e157" rowspan="1">
    Name
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d166663e160" rowspan="1">
    Description
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d166663e163" rowspan="1">
    Reset
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [31:19]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__31-19-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [18]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PWR_ACTIVE_EDGE_IRQ10
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if power mode DEVPACTIVE[10] input caused the input edge event.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[10] input (DBG_RECOV) did not assert the interrupt output.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[10] input (DBG_RECOV) asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-18-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [17]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PWR_ACTIVE_EDGE_IRQ9
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if power mode DEVPACTIVE[9] input caused the input edge event.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[9] input (WARM_RST) did not assert the interrupt output.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[9] input (WARM_RST) asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-17-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [16]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PWR_ACTIVE_EDGE_IRQ8
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if power mode DEVPACTIVE[8] input caused the input edge event.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[8] input (ON) did not assert the interrupt output.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[8] input (ON) asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-16-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [15]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PWR_ACTIVE_EDGE_IRQ7
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if power mode DEVPACTIVE[7] input caused the input edge event.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[7] input (FUNC_RET) did not assert the interrupt output.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[7] input (FUNC_RET) asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-15-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [14]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__14-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [13]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PWR_ACTIVE_EDGE_IRQ5
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if power mode DEVPACTIVE[5] input caused the input edge event.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[5] input (FULL_RET) did not assert the interrupt output.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[5] input (FULL_RET) asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-13-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [12:10]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__12-10-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [9]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    PWR_ACTIVE_EDGE_IRQ1
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates if power mode DEVPACTIVE[1] input caused the input edge event.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[1] input (OFF_EMU) did not assert the interrupt output.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       DEVPACTIVE[1] input (OFF_EMU) asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-9-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [8]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__8-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [7]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    OTHER_IRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Indicates there is an interrupt event pending in the Additional Interrupt Status Register (PPU_AISR).
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No interrupt pending in PPU_AISR.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       Interrupt pending in PPU_AISR.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-7-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [6]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    Reserved
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__6-reset" rowspan="1">
    <span class="documents-archterm">
     RES0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [5]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    LOCKED_IRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Locked event status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No locked event.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       A locked event asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-5-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [4]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    EMU_DENY_IRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Emulated transition denial event status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No emulated transition denial event.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An emulated transition denial event asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-4-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [3]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    EMU_ACCEPT_IRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Emulated transition acceptance event status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No emulated transition acceptance event.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       An emulated transition acceptance event asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-3-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [2]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    STA_DENY_IRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Static transition denial event status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No static transition denial event.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       A static transition denial event asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-2-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    [1]
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    STA_ACCEPT_IRQ
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Static transition acceptance event status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No static transition acceptance event.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       A static transition acceptance event asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cell-norowborder" colspan="1" id="lsb1733415054921__id-1-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    [0]
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    STA_POLICY_TRN_IRQ
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Static full policy transition completion event status.
    </p>
    <dl>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b0
      </span>
     </dt>
     <dd>
      <p>
       No static full policy transition completion event.
      </p>
     </dd>
     <dt class="documents-dlterm">
      <span class="documents-g.number.bin">
       0b1
      </span>
     </dt>
     <dd>
      <p>
       A static full policy transition completion event asserted the interrupt output.
      </p>
     </dd>
    </dl>
   </td>
   <td class="documents-cellrowborder" colspan="1" id="lsb1733415054921__id-0-reset" rowspan="1">
    <span class="documents-g.number.bin">
     0b0
    </span>
   </td>
  </tr>
 </tbody>
</table>

### Accessibility

This interface is accessible as follows:

RW
