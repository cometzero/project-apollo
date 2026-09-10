# Programming considerations

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Programming-considerations>

### Programming considerations

The DMA channels can be configured to transfer several data elements from one location to another. There are multiple settings for every command that define the way the DMAC sends the transfers to the bus interface.

TRANSIZE setting adjusts the size of the data elements the command moves. The setting is the same for both read and write directions and ranging in power of 2 steps from a single byte to the number of bytes that fit into the DATA\_WIDTH of the bus interface. This sets the base for all internal counters, the address increment logic, and the burst calculation logic.

The XSIZE setting defines the number of data elements moved in the X direction. For 1D transfers, this is the total number of transfers. For 2D transfers, this is the length of a line so the total number of transfers can be calculated by XSIZE \* YSIZE.

> ### Note
>
> The DMAC generates bursts so that they do not cross between lines. So that after completing a line, the DMAC starts transferring the next line with a separate burst.

The TRIGINBLKSIZE register field adjusts the maximum number of elements sent for a block trigger request. This can be used to split up the command into smaller parts. The total number of elements in the command is not necessarily a multiple of TRIGINBLKSIZE so partial blocks can also be sent at the end of a command. The TRIGINBLKSIZE setting can be different on source and destination sides which may result in having partial data stored temporarily in the FIFO until the triggers are acknowledged.

For example, the SRCTRIGINBLKSIZE is 5 and DESTRIGINBLKSIZE is 8, that results in having 2 triggers on the source side that generate enough data to the destination side but leaves 2 data elements in the FIFO until the next destination trigger is received.

1. Source trigger received – 5 elements read, FIFO level increased to 5.
2. Source trigger received – 5 elements read, FIFO level increased to 10.
3. Destination trigger received – 8 elements written, FIFO level decreased to 2.

Trigger events can happen in parallel and it depends on the FIFO size and its actual level whether the read or write side of the channel must wait for the other side to finish. Care must be taken when programming the trigger block size settings for timing critical applications.

The MAXBURSTLEN field limits the maximum number of beats sent out by the DMAC on the bus interface for a burst request. This setting can be used to adjust the bus utilization during the command and also creates arbitration points when multiple channels try to access the bus concurrently.

Based on these settings one example DMA command consists of XSIZE number of TRANSIZE-based data elements. This command can be split into several blocks defined by TRIGINBLKSIZE which can also be split into multiple bursts limited by the MAXBURSTLEN. The following example shows how the XSIZE=20, TRIGINBLKSIZE=7 and MAXBURSTLEN=3 settings affect the command execution. Trigger blocks and bursts are only defined to have a maximum size so the DMA command may send smaller trigger blocks and bursts as it is seen in the figure.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Using different sizes in a command
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-cell-norowborder" colspan="8" id="d46522e123" rowspan="1">
    <p>
     XSIZE = 20
    </p>
   </th>
  </tr>
  <tr>
   <th class="documents-nocellnorowborder" colspan="3" id="d46522e130" rowspan="1">
    <p>
     TRIGINBLKSIZE = 7
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="3" id="d46522e134" rowspan="1">
    <p>
     TRIGINBLKSIZE = 7
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="2" id="d46522e138" rowspan="1">
    <p>
     TRIGINBLKSIZE = 6
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BURST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BURST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BURST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BURST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BURST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BURST
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BURST
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     BURST
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     1
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     3
    </p>
   </td>
  </tr>
 </tbody>
</table>

The DMAC selects the largest burst possible to reduce the number of address requests on the bus, but this can be limited if the bandwidth or latency requirements require adjustments from software.

Besides DATA\_WIDTH, TRANSIZE, XSIZE, TRIGINBLKSIZE and MAXBURSTLEN, burst generation is also aﬀected by the following factors:

- The size of the FIFO within a DMA channel limits the maximum amount of data in a burst. The DMA channels only generate bursts that do not exceed half of the capacity of the corresponding Data FIFO. This limitation mitigates latency on write and read AXI buses and so enables gapless command execution within a line.
- To enable easier AXI to AHB conversion, the DMAC only generates bursts that do not cross the 1kB address boundary.
- Certain transfer properties such as transfer type (device or memory) and aligned or unaligned starting and ending addresses might also affect how the DMAC generates bursts, as the DMAC will try to optimize bandwidth by utilizing as much of the bus width as possible and will group transfers if it can.

For more details, see [AXI bandwidth utilization](/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/AXI-bandwidth-utilization?lang=en "This section provides a definition of terms used and optimization requirements.").
