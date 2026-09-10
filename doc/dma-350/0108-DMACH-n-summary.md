# DMACH<n> summary

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-summary/DMACH-n--summary>

### DMACH<n> summary

DMA Channel Register Frame.

This block contains the channel registers related to the execution of the DMA command. When the registers for the command are configured and the ENABLECMD is set, then most of the registers become read-only except for a few that allow control from the SW during the operation of the command.

The following global constraints apply to all registers in this block:

- When the channel is set to Secure, Non-secure accesses to this register block are not allowed and response is based on the security configuration settings.
- When the channel is set to privileged, then unprivileged accesses to this register block are treated as RAZ/WI.
- Base address: 0x1000 + 0x0100 \* <n>
- Size: 0x0100
- Instances: NUM\_CHANNELS

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DMACH&lt;n&gt; register summary
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d7988e117" rowspan="1">
    <p>
     Offset
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7988e121" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7988e125" rowspan="1">
    <p>
     Type
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7988e129" rowspan="1">
    <p>
     Default
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d7988e133" rowspan="1">
    <p>
     Width
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d7988e138" rowspan="1">
    <p>
     Description
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_CMD
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-CMD?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-CMD?lang=en" title="The Channel DMA Command register allows the SW to control the operation of a DMA command.">
      CH_CMD
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x04
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_STATUS
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-STATUS?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-STATUS?lang=en" title="The Channel Status register shows the internal status of the DMA command and also reports interrupts about internal events.">
      CH_STATUS
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x08
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_INTREN
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-INTREN?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-INTREN?lang=en" title="The Channel Interrupt Enable register can enable the interrupt generation for internal events.">
      CH_INTREN
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x0C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_CTRL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00200200
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-CTRL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-CTRL?lang=en" title="The Channel Control register can be used to configure the type of the transfers and the resources needed by the currently executed DMA command. It also defines how the command shall behave when the command is complete.">
      CH_CTRL
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x10
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_SRCADDR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCADDR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCADDR?lang=en" title="The Channel Source Address register defines the 32-bit base address of the command to read the data from. When the register is read during the execution of the command it shows an approximate hint at the actual address the DMA channel is going to read from.">
      CH_SRCADDR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x14
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_SRCADDRHI
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCADDRHI?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCADDRHI?lang=en" title="The Channel Source Address Register High Bits [63:32] defines the upper 32 bits of the read address if more than 32-bit addressing is used in the system. When the register is read during the execution of the command it shows an approximate hint at the actual address the DMA channel is going to read from.">
      CH_SRCADDRHI
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x18
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_DESADDR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESADDR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESADDR?lang=en" title="The Channel Destination Address register defines the 32-bit base address of the command to write the data to. When the register is read during the execution of the command it shows an approximate hint at the actual address the DMA channel is going to write to.">
      CH_DESADDR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x1C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_DESADDRHI
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESADDRHI?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESADDRHI?lang=en" title="The Channel Destination Address Register, High Bits [63:32], defines the upper 32 bits of the write address if more than 32-bit addressing is used in the system. When the register is read during the execution of the command it shows an approximate hint at the actual address the DMA channel is going to write to.">
      CH_DESADDRHI
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x20
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_XSIZE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XSIZE?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XSIZE?lang=en" title="The Channel X Dimension Size Register, Lower Bits [15:0] register defines the number of data units copied during the DMA command up to 16 bits in the X dimension. The source and destination size of the command may be different for some transfer types. When read during the execution of the DMA command, the register shows an approximate hint of the remaining number of lines in both read and write directions.">
      CH_XSIZE
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x24
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_XSIZEHI
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XSIZEHI?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XSIZEHI?lang=en" title="The Channel X Dimension Size Register, High Bits [31:16] defines the number of data units copied during the DMA command up to 32 bits in the X dimension. The source and destination size of the command may be different for some transfer types. When read during the execution of the DMA command, the register shows an approximate hint of the remaining number of lines in both read and write directions.">
      CH_XSIZEHI
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x28
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_SRCTRANSCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x000F0400
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTRANSCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTRANSCFG?lang=en" title="The Channel Source Transfer Configuration register provides transfer attribute settings in the read direction of the DMA command.">
      CH_SRCTRANSCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x2C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_DESTRANSCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x000F0400
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTRANSCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTRANSCFG?lang=en" title="The Channel Destination Transfer Configuration register provides transfer attribute settings in the write direction of the DMA command.">
      CH_DESTRANSCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x30
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_XADDRINC
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XADDRINC?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XADDRINC?lang=en" title="The Channel X Dimension Address Increment register sets the increment values used to update the source and destination addresses after each transferred data unit.">
      CH_XADDRINC
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x34
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_YADDRSTRIDE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-YADDRSTRIDE?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-YADDRSTRIDE?lang=en" title="The Channel Y Dimension Address Stride register sets the increment values used to update the source and destination line base addresses after each line is transferred.">
      CH_YADDRSTRIDE
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x38
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_FILLVAL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-FILLVAL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-FILLVAL?lang=en" title="The Channel Fill Pattern Value register provides a predefined value to be used to fill the remaining part of the destination memory area when the source side of the command is finished.">
      CH_FILLVAL
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x3C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_YSIZE
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-YSIZE?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-YSIZE?lang=en" title="The Channel Y Dimensions Size register defines the number of lines copied during the DMA command up to 16 bits in the Y dimension. The read and write size of the command may be different for some transfer types. When read during the execution of the DMA command, the register shows an approximate hint of the remaining number of lines in both read and write directions.">
      CH_YSIZE
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x40
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_TMPLTCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-TMPLTCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-TMPLTCFG?lang=en" title="The Channel Template Configuration register provides configuration settings when using template pattern based copy operations.">
      CH_TMPLTCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x44
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_SRCTMPLT
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000001
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTMPLT?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTMPLT?lang=en" title="The Channel Source Template Pattern register sets the template pattern used for reading the source memory area.">
      CH_SRCTMPLT
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x48
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_DESTMPLT
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000001
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTMPLT?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTMPLT?lang=en" title="The Channel Destination Template Pattern register sets the template pattern used for writing the destination memory area.">
      CH_DESTMPLT
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x4C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_SRCTRIGINCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTRIGINCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTRIGINCFG?lang=en" title="The Channel Source Trigger In Configuration register provides configuration settings when using source side trigger input for the current DMA command.">
      CH_SRCTRIGINCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x50
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_DESTRIGINCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTRIGINCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTRIGINCFG?lang=en" title="The Channel Destination Trigger In Configuration register provides configuration settings when using destination side trigger input for the current DMA command.">
      CH_DESTRIGINCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x54
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_TRIGOUTCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-TRIGOUTCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-TRIGOUTCFG?lang=en" title="The Channel Trigger Out Configuration register provides configuration settings when using trigger output for the current DMA command.">
      CH_TRIGOUTCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x58
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_GPOEN0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOEN0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOEN0?lang=en" title="The Channel GPO Driving Enable register 0 enables which GPO ports are enabled to change at the beginning of current DMA command. GPO ports from bit 0 to 31 can be enabled by this register if the port is available to this channel.">
      CH_GPOEN0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x60
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_GPOVAL0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOVAL0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOVAL0?lang=en" title="The Channel GPO Value register 0 sets the value to be driven on the GPO ports that are enabled at the beginning of current DMA command. The value of the GPO ports from bit 0 to 31 can be adjusted by this register if the port is available to this channel.">
      CH_GPOVAL0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x68
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_STREAMINTCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-STREAMINTCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-STREAMINTCFG?lang=en" title="The Channel Stream Interface Configuration register provides configuration settings for the stream interface used by the current DMA command.">
      CH_STREAMINTCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x70
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_LINKATTR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKATTR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKATTR?lang=en" title="The Channel Link Address Memory Attributes register provides transfer attribute settings for the command link related read transfers. The security and privilege attributes cannot be adjusted, they match the attributes of the channel.">
      CH_LINKATTR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x74
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_AUTOCFG
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-AUTOCFG?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-AUTOCFG?lang=en" title="The Channel Automatic Command Restart Configuration register configures the automatic restart behavior of the currently running command.">
      CH_AUTOCFG
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x78
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_LINKADDR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKADDR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKADDR?lang=en" title="The Channel Link Address register sets the 32-bit address of the next element in a command link. When the command execution is finished and this register is set then the DMA channel starts loading the next command from this address.">
      CH_LINKADDR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x7C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_LINKADDRHI
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKADDRHI?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKADDRHI?lang=en" title="The Channel Link Address Register, High Bits [63:32] sets the upper address bits of the next element in a command link.">
      CH_LINKADDRHI
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x80
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_GPOREAD0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOREAD0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOREAD0?lang=en" title="The Channel GPO Read Value register 0 shows the current value of the GPO ports from bit 0 to 31 that are available to this channel.">
      CH_GPOREAD0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x88
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_WRKREGPTR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-WRKREGPTR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-WRKREGPTR?lang=en" title="The Channel Working Register Pointer register can be used to select an internal work register of the DMA channel that is visible in the CH_WRKREGVAL register.">
      CH_WRKREGPTR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x8C
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_WRKREGVAL
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-WRKREGVAL?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-WRKREGVAL?lang=en" title="The Channel - Working Register Value register shows the internal value of a work register of the DMA channel selected by the CH_WRKREGPTR register.">
      CH_WRKREGVAL
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x90
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_ERRINFO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0x00000000
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-ERRINFO?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-ERRINFO?lang=en" title="The Channel Error Information register provides information about internal errors encountered during command execution by the DMA channel.">
      CH_ERRINFO
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xC8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_IIDR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPL_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-IIDR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-IIDR?lang=en" title="The Channel Implementation Identification register provides information about the revision of the product implementing the DMA channel.">
      CH_IIDR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xCC
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_AIDR
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPL_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-AIDR?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-AIDR?lang=en" title="The Channel Architecture Identification register provides information about the architecture version supported by the DMA channel.">
      CH_AIDR
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xE8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_ISSUECAP
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RW
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPL_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-ISSUECAP?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-ISSUECAP?lang=en" title="Used for setting issuing capability threshold.">
      CH_ISSUECAP
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xF8
     </span>
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CH_BUILDCFG0
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     IMPL_DEF
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-BUILDCFG0?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-BUILDCFG0?lang=en" title="The Channel Build Configuration and Capability register 0 contains the configuration parameters and capabilities of the DMA channel.">
      CH_BUILDCFG0
     </a>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     <span class="documents-g.number.hex">
      0xFC
     </span>
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     CH_BUILDCFG1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     RO
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     IMPL_DEF
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     32
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     See
     <a class="document-topic" document-topic-path="/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-BUILDCFG1?lang=en" href="/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-BUILDCFG1?lang=en" title="The Channel Build Configuration and Capability register 1 contains the configuration parameters and capabilities of the DMA channel.">
      CH_BUILDCFG1
     </a>
    </p>
   </td>
  </tr>
 </tbody>
</table>
