# CH_CTRL

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-CTRL>

### CH\_CTRL

The Channel Control register can be used to configure the type of the transfers and the resources needed by the currently executed DMA command. It also defines how the command shall behave when the command is complete.

The content of this register can be updated during command linking by setting bit[3] in the command link header.

### Configurations

See bit descriptions.

### Attributes

Register frame
:   DMACH<n>

Offset
:   0x00C

Type
:   RW

Default
:   0x00200200

### Usage constraints

Becomes read-only after ENABLECMD is set.

### Bit descriptions

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   CH_CTRL register bit descriptions
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d53881e129" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53881e133" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53881e137" rowspan="1">
    <p>
     Description
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d53881e141" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d53881e145" rowspan="1">
    <p>
     Default
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [31:30]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [29]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     USESTREAM
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable Stream Interface use for this command.
    </p>
    <ul>
     <li>
      <p>
       0: disable
      </p>
     </li>
     <li>
      <p>
       1: enable
      </p>
     </li>
    </ul>
    <p>
     The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: CH_STREAM_EN
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [28]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     USEGPO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable GPO use for this command.
    </p>
    <ul>
     <li>
      <p>
       0: disable
      </p>
     </li>
     <li>
      <p>
       1: enable
      </p>
     </li>
    </ul>
    <p>
     The field is
     <span class="documents-archterm">
      RAZ/WI
     </span>
     when the following condition is False: (CH_GPO_EN * GPO_WIDTH) &gt; 0.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [27]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     USETRIGOUT
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable Trigger Output use for this command.
    </p>
    <ul>
     <li>
      <p>
       0: disable
      </p>
     </li>
     <li>
      <p>
       1: enable
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [26]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     USEDESTRIGIN
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable Destination Trigger Input use for this command.e
    </p>
    <ul>
     <li>
      <p>
       0: disable
      </p>
     </li>
     <li>
      <p>
       1: enable
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [25]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     USESRCTRIGIN
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Enable Source Trigger Input use for this command:
    </p>
    <ul>
     <li>
      <p>
       0: disable
      </p>
     </li>
     <li>
      <p>
       1: enable
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [24]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DONEPAUSEEN
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Done pause enable. When set to HIGH the assertion of the STAT_DONE flag results in an automatic pause request for the current DMA operation. When the paused state is reached the STAT_RESUMEWAIT flag is also set. When set to LOW the assertion of the STAT_DONE does not pause the progress of the command and the next operation of the channel is started immediately after the STAT_DONE flag is set.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [23:21]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     DONETYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Done type selection. This field defines when the STAT_DONE status flag is asserted during the command operation.
    </p>
    <ul>
     <li>
      <p>
       000: STAT_DONE flag is not asserted for this command.
      </p>
     </li>
     <li>
      <p>
       001: End of a command, before jumping to the next linked command. (default)
      </p>
     </li>
     <li>
      <p>
       011: End of an autorestart cycle, before starting the next cycle.
      </p>
     </li>
     <li>
      <p>
       Others : Reserved.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [20:18]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     REGRELOADTYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Automatic register reload type. Defines how the DMA command reloads initial values at the end of a DMA command before autorestarting, ending or linking to a new DMA command:
    </p>
    <ul>
     <li>
      <p>
       000: Reload Disabled.
      </p>
     </li>
     <li>
      <p>
       001: Reload source and destination size registers only.
      </p>
     </li>
     <li>
      <p>
       011: Reload source address only and all source and destination size registers.
      </p>
     </li>
     <li>
      <p>
       101: Reload destination address only and all source and destination size registers.
      </p>
     </li>
     <li>
      <p>
       111: Reload source and destination address and all source and destination size registers.
      </p>
     </li>
     <li>
      <p>
       Others: Reserved.
      </p>
     </li>
    </ul>
    <p>
     NOTE: When CLEARCMD is set, the reloaded registers are also cleared.
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [17:15]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [14:12]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     YTYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Operation type for Y direction:
    </p>
    <ul>
     <li>
      <p>
       000: &ldquo;disable&rdquo; - Only do 1D transfers. When HAS_2D is 0, meaning 2D capability is not supported in HW, the YTYPE is always &ldquo;000&rdquo;.
      </p>
     </li>
     <li>
      <p>
       001: &ldquo;continue&rdquo; - Copy 2D data in a continuous manner from source area to the destination area by using the YSIZE registers. The copy stops when the source runs out of data or the destination runs out of space. Not supported when HAS_2D is 0 in HW.
      </p>
     </li>
     <li>
      <p>
       010: &ldquo;wrap&rdquo; - Wrap the 2D source area within the destination 2D area by starting to copy data from the beginning of the first source line to the remaining space in the destination area. If the destination area is smaller than the source area then the behavior is UNPREDICTABLE. Not supported when HAS_WRAP or HAS_2D is 0 in HW.
      </p>
     </li>
     <li>
      <p>
       011: Fill the remainder of the destination area with FILLVAL when the source area runs out of data. If the destination area is smaller than the source area then the behavior is UNPREDICTABLE. Not supported when HAS_WRAP or HAS_2D is 0 in HW.
      </p>
     </li>
     <li>
      <p>
       Others: Reserved The field is
       <span class="documents-archterm">
        RAZ/WI
       </span>
       when extended features are disabled for the channel.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [11:9]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     XTYPE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Operation type for X direction:
    </p>
    <ul>
     <li>
      <p>
       000: &ldquo;disable&rdquo; - No data transfer takes place for this command. This mode can be used to create empty commands that wait for an event or set GPOs.
      </p>
     </li>
     <li>
      <p>
       001: &ldquo;continue&rdquo; - Copy data in a continuous manner from source to the destination. For 1D operations it is expected that SRCXSIZE is equal to DESXSIZE, other combinations result in UNPREDICTABLE behavior. For 2D operations, this mode can be used for simple 2D to 2D copy but it also allows the reshaping of the data like 1D to 2D or 2D to 1D conversions. If the DESXSIZE is smaller than SRCXSIZE then the read data from the current source line goes to the next destination line. If SRCXSIZE is smaller than DESXSIZE then the reads start on the next line and data is written to the remainder of the current destination line. Note: For 1D to 2D the SRCYSIZE for 2D to 1D conversion the DESYSIZE needs to be set to 1 when using this mode.
      </p>
     </li>
     <li>
      <p>
       010: &ldquo;wrap&rdquo; - Wrap source data within a destination line when the end of the source line is reached. Read starts again from the beginning of the source line and copied to the remainder of the destination line. If the DESXSIZE is smaller than SRCXSIZE then the behavior is UNPREDICTABLE. Not supported when HAS_WRAP is 0 in HW.
      </p>
     </li>
     <li>
      <p>
       011: &ldquo;fill&rdquo; - Fill the remainder of the destination line with FILLVAL when the end of the source line is reached. If the DESXSIZE is smaller than SRCXSIZE then the behavior is UNPREDICTABLE. Not supported when HAS_WRAP is 0 in HW.
      </p>
     </li>
     <li>
      <p>
       Others: Reserved.
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [8]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [7:4]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CHPRIO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Channel Priority.
    </p>
    <ul>
     <li>
      <p>
       0: Lowest Priority
      </p>
     </li>
     <li>
      <p>
       15: Highest Priority
      </p>
     </li>
    </ul>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [3]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     [2:0]
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     TRANSIZE
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     The width of this field depends on CoreLink DMA-350&rsquo;s DATA_WIDTH config parameter.
    </p>
    <p>
     If DATA_WIDTH is 128, bits[2:0] are present. In this case, SW can program all three bits, though the DMAC does not support TRANSIZE values larger than 128 bits. If DATA_WIDTH is 64 or 32, then bit[2] is RESERVED and only bits[1:0] are present. In this case, SW can program only the two least significant bits as the DMAC handles the most significant bit as
     <span class="documents-archterm">
      RAZ/WI
     </span>
     .
    </p>
    <p>
     Transfer Entity Size. Size in bytes = 2^TRANSIZE.
    </p>
    <ul>
     <li>
      <p>
       000: Byte
      </p>
     </li>
     <li>
      <p>
       001: Halfword
      </p>
     </li>
     <li>
      <p>
       010: Word
      </p>
     </li>
     <li>
      <p>
       011: Doubleword
      </p>
     </li>
     <li>
      <p>
       100: 128bits
      </p>
     </li>
     <li>
      <p>
       101: 256bits
      </p>
     </li>
     <li>
      <p>
       110: 512bits
      </p>
     </li>
     <li>
      <p>
       111: 1024bits
      </p>
     </li>
    </ul>
    <p>
     Note that DATA_WIDTH limits this field. Address is aligned to TRANSIZE by the DMAC by ignoring the lower bits.
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0
     </span>
    </p>
   </td>
  </tr>
 </tbody>
</table>
