# Command execution status reporting

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMA-Channel-lifecycle/Command-execution-status-reporting>

### Command execution status reporting

The software can read the contents of X, Y size, and address registers after the DMA command execution.

The contents of these registers depend on the manner of DMA command stop:

DONE status reached - command execution was completed:

- Size registers are 0, no more transactions to be completed on either read or write side.
- Address registers contain the next address as if there were subsequent DMAC operations of the same type as the completed command.

STOPPED/PAUSED status - command execution was stopped or paused before execution completed:

- Size registers contain the actual coordinate of the current transaction that was not completed.
- Address registers contain the address of the next transaction that was not completed.

In STOPPED/PAUSED state, address and size register values are only approximations of the actual command execution status, and might not contain the exact position. They serve as a hint about where approximately the command execution was halted.

If pausing occurs during command link execution, the registers read back might contain an incoherent command, because not all registers might be updated when the DMA enters PAUSED state.

### Address register at the end of command

At the end of command, address registers contain the address of the next DMAC transaction of the same type that was not completed. If the command is completed, the next address points to the address that would have been used for the transaction if the command contained more transactions.

Major cases are covered in the following tables for clarification.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Read operations
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
   <th class="documents-nocellnorowborder" colspan="1" id="d49417e120" rowspan="1">
    <p>
     Read
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d49417e124" rowspan="1">
    <p>
     DMA command last line end
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d49417e128" rowspan="1">
    <p>
     DMA command not last line end
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d49417e132" rowspan="1">
    <p>
     DMA command mid-line
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1D without wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     N/A
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1D with wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Cur_line_start_addr
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     N/A
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2D with Y not wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Incr_line_start_addr
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Incr_line_start_addr
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     2D with Y wrap
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     First_line_start_addr
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Incr_line_start_addr
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
  </tr>
 </tbody>
</table>

When X type is wrap, 1D with wrap or 2D with Y wrap, there are two possible line ends for read:

- When read line is ended only, next address is always the start address of the same line.
- When write line is ended, with or without read line ending at the same time, the next address is determined by the read operations in the preceding table.

Because 1D commands consist of only one line, it is also deemed as the last line.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   Write operations
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
   <th class="documents-nocellnorowborder" colspan="1" id="d49417e257" rowspan="1">
    <p>
     Write
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d49417e261" rowspan="1">
    <p>
     DMA command last line end
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d49417e265" rowspan="1">
    <p>
     DMA command not last line end
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d49417e269" rowspan="1">
    <p>
     DMA command mid-line
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1D without wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     N/A
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     1D with wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     N/A
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     2D with Y not wrap
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Incr_line_start_addr
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Incr_line_start_addr
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     2D with Y wrap
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Incr_line_start_addr
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Incr_line_start_addr
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Incr_addr
    </p>
   </td>
  </tr>
 </tbody>
</table>

Command line definitions:

Incr\_addr
:   Increment the address of the last DMAC transaction based on increment or template configurations and configured TRANSIZE.

Incr\_line\_start\_addr
:   Increment the starting address of current line based on Y stride and TRANSIZE configurations. Address points to the first byte of this line.

Cur\_line\_start\_addr
:   Address points to starting byte of current line.

First\_line\_start\_addr
:   Address points to the first byte of the first line in the current 2D DMA command.

DMA command last line end
:   Last transaction of the command executed by DMA in this direction is the last transaction of the last line.

DMA command not last line end
:   Last transaction of the command executed by DMA in this direction is the last transaction of a line.

DMA command mid-line
:   Last transaction of the command executed by DMA in this direction is the not last transaction of a line.

### Examples

1D command without wrap for read/write:

- X type: continue/fill
- Y type: disabled
- X size: 5
- Y size: -
- Transize: 1 byte
- Start address: 0x0

If last read/write transaction address of command: 0x4, (5. byte), both addresses point to 0x5 when software reads their values back.

1D command with wrap for read/write:

- X type: wrap
- Y type: disabled
- Source X size: 5
- Dest. X size: 7
- Y size: -
- Transize: 1 byte
- Start address: 0x0
  - If last read transaction address of command: 0x4, (5. read byte), read address points to 0x0 when software reads its value back.
  - If last read transaction address of command: 0x1, (2. read byte), read address points to 0x2 when software reads its value back.
  - If last read transaction address of command: 0x1, (7. read byte), read address points to 0x0 when software reads its value back (destination size reached for wrap).
  - If last write transaction address of command: 0x6, (7. write byte), write address points to 0x7 when software reads its value back.

2D command without wrap for read/write:

- X type: continue/fill
- Y type: continue/fill
- X size: 5
- Y size: 3
- Y stride: 0x10
- Transize: 1 byte
- Start address: 0x0
  - If last read/write transaction address of command: 0x24, (3. line, 5. byte), read/write addresses point to 0x30 when software reads their values back.
  - If last read/write transaction address of command: 0x14, (2. line, 5. byte), read/write addresses point to 0x20 when software reads their values back.
  - If last read/write transaction address of command: 0x13, (2. line, 4. byte), read/write addresses point to 0x14 when software reads their values back.

2D command with wrap for read/write:

- X type: continue/fill
- Y type: wrap
- Source X size: 5
- Y size: 3
- Y stride: 0x10
- Transize: 1 byte
- Start address: 0x0
  - If last read/write transaction address of command: 0x24, (3. line, 5. byte), read address points to 0x0 and write address points to 0x30 when software reads their values back.
  - If last read/write transaction address of command: 0x14, (2. line, 5. byte), read/write addresses point to 0x20 when software reads their values back.
  - If last read/write transaction address of command: 0x13, (2. line, 4. byte), read/write addresses point to 0x14 when software reads their values back.

2D command with wrap for read/write:

- X type: wrap
- Y type: wrap
- Source X size: 5
- Dest. X size: 7
- Y size: 3
- Y stride: 0x10
- Transize: 1 byte
- Start address: 0x0
  - If last read transaction address of command: 0x24, (3. line, 5. read byte), read address points to 0x20 when software reads its value back.
  - If last read transaction address of command: 0x21, (3. line, 2. read byte), read address points to 0x22 when software reads its value back.
  - If last read transaction address of command: 0x21, (3. line, 7. read byte), read address points to 0x0 when software reads its value back.
  - If last read transaction address of command: 0x11, (2. line, 2. read byte), read address points to 0x12 when software reads its value back.
  - If last read transaction address of command: 0x11, (2. line, 7. read byte), read address points to 0x20 when software reads its value back.
- Write addresses work the same way as in 2D wrap with not 1D wrap case.

### Addresses after empty commands

Read/write addresses remain unchanged, if their respective direction was not involved in command execution.

For example, when write is active but read is inactive in a DMA command, the read address does not change but the write address does change according to the behavior described above.

### Size registers at the end of command

Size registers contain the coordinates of last unprocessed transaction within the current line. Both size registers are 0 when the DMA command completes.

When a stop or bus error interrupts the DMA command, 1D commands only have X registers and they contain the remaining unsent DMAC transactions in TRANSIZE.

2D commands have X and Y size registers, and they contain the X and Y coordinates of the next unsent transaction:

- When the DMA command is mid-line, the X and Y sizes contain the unsent coordinates of the next unsent data.
- When the DMA command has completed the current line, depending on the timing of the interrupting event, both following coordinates are possible. These coordinates are equivalent, as they indicate the same amount of data that was not transmitted from the DMA command.

  - Y: current line number, X:0
  - Y: next line number, X: total X-size of the line

Additionally, X and Y sizes can be optimized for certain Y and X configurations at the beginning of the DMA command:

- IF X type is WRAP or FILL and destination X-size < source X-size, source X-size is set to destination X-size.
- If X type is WRAP or FILL and Y type is FILL or CONTINUE, and source Y-size > destination Y-size, source Y-size is set to destination X-size.

These optimizations help reduce unnecessary read operations that can already be predicted from the DMA command configuration.

### Size after empty commands

If there is an empty command execution, sizes do not change at the end of DMA command. If either side is involved in command execution while the other remains idle, size registers on the idle side become zero when the command is completed.
