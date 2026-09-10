# Interworking with Trigger Interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/AXI4-stream-operation/Stream-interworking-with-other-modes/Interworking-with-Trigger-Interface>

### Interworking with Trigger Interface

The stream interface usage has some restrictions on the trigger input interface as the block-based transfers might behave improperly when converting them to stream output transfers.

The whole stream out transfer is one packet, which cannot have strobes in the middle of the packet. Therefore any block, or single beat transfer will stall the interface if it is not aligned to the data width of the stream interface. If the DMAC fetches the remaining data, but it is stored in an internal FIFO, the external stream engine does not have all the data to process until the next block is triggered.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   Stream interface for triggers
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
   <th class="documents-nocellnorowborder" colspan="1" id="d68140e74" rowspan="1">
    <p>
     Mode
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d68140e78" rowspan="1">
    <p>
     SRC/DESTRIGINTYPE
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d68140e82" rowspan="1">
    <p>
     Stream allowed
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d68140e86" rowspan="1">
    <p>
     Comment
    </p>
   </th>
  </tr>
 </thead>
 <tbody>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Software Controlled only Command Trigger
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     000
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Yes
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     SW can initiate the whole command that uses the stream interface in any direction.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     HW Controlled Command trigger
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     100
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Yes
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     HW can initiate the whole command that uses the stream interface in any direction.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Any Flow control trigger
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     001, 101, 110
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     No
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Stream interface cannot stall or strobe non-data width aligned trigger block size settings.
    </p>
   </td>
  </tr>
 </tbody>
</table>

> ### Note
>
> SRC/DESTRIGINTYPE values are defined in the [CH\_DESTRIGINCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTRIGINCFG?lang=en "The Channel Destination Trigger In Configuration register provides configuration settings when using destination side trigger input for the current DMA command.") section of the [Programmers model](/documentation/102482/0000/Programmers-model?lang=en "This section describes the functionality of the DMA-350 from a programming perspective.").

If packet based triggering is required from a peripheral, the SRCXSIZE or DESXSIZE must be set to match the size of a single packet and the command is reloaded for the next packet. This is to replace a large XSIZE setting for multiple packets with using BLOCK triggers where TRIGBLOCKSIZE represents one single packet.

Trigger out signaling can be used without any restrictions when using the stream interface. Trigger loops can only be used to start whole commands on the receiving side as flow control is not supported.
