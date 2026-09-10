# Error handling

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMA-Channel-lifecycle/Error-handling>

### Error handling

There are four types of errors that can occur during DMAC operation:

- AXI5 bus error during operation
- Configuration error
- Trigger selection error during trigger allocation
- AXI-Stream interface error during operation

Any of these errors causes the DMA channel to stop its operation. The error status flag, STAT\_ERR, is set in the CH<x>\_STATUS register when the channel state transitions to DISABLED (ch\_enabled = 1’b0).

If the related interrupt enable flag is set, INTREN\_ERR, the interrupt flag is also asserted, INT\_ERR.

The cause of the error is indicated in the CH<x>\_ERRINFO register which contains valid information when STAT\_ERR is asserted.

The following table lists the possible errors indicated through the CH<x>\_ERRINFO register.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 1.
   </span>
   DMA-350 channel errors
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d59607e104" rowspan="1">
    <p>
     Error type
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d59607e108" rowspan="1">
    <p>
     CH&lt;x&gt;_ERRINFO field
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d59607e112" rowspan="1">
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
     Bus errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     BUSERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Error occurred on any of the AXI managers or AXI-Stream interfaces during data transfer or command link fetch. The exact cause is indicated in the AXI*ERR fields, see the table below.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Configuration errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     CFGERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     The command that is about to be executed has an invalid configuration in the registers, or invalid command link header was received. See LINKHDRERR, REGVALERR, and CFGCONFLERR fields for the exact cause and the table detailing the error information below.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger in selection errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     SRCTRIGINSELERR, DESTRIGINSELERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     A trigger input port selected by the channel is already in use by another enabled channel or by the trigger matrix.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     Trigger out selection errors
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     TRIGOUTSELERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     A trigger output port selected by the channel is already in use by another enabled channel or by the trigger matrix.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     Stream overflow error
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     STREAMERR
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     The stream interface encountered an error. See STR*ERR fields for the exact cause of the error.
    </p>
   </td>
  </tr>
 </tbody>
</table>

The following ERRINFO fields give additional information on the reasons for the errors indicated in the CH<x>\_ERRINFO register. Bit offsets are relative to CH<x>\_ERRINFO register.

<table>
 <caption>
  <span class="documents-tablecap">
   <span class="documents-table--title-label">
    Table 2.
   </span>
   DMA-350 channel error reasons - ERRINFO fields
  </span>
 </caption>
 <colgroup>
  <col span="1"/>
  <col span="1"/>
  <col span="1"/>
 </colgroup>
 <thead>
  <tr>
   <th class="documents-nocellnorowborder" colspan="1" id="d59607e218" rowspan="1">
    <p>
     Bits
    </p>
   </th>
   <th class="documents-nocellnorowborder" colspan="1" id="d59607e222" rowspan="1">
    <p>
     Name
    </p>
   </th>
   <th class="documents-cell-norowborder" colspan="1" id="d59607e226" rowspan="1">
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
     [31:27]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
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
     CFGCONFLERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Configuration error because there are conflicting settings in the configuration registers.
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
     REGVALERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Configuration error because one of the configuration registers is set to an illegal value.
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
     LINKHDRERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Configuration error because an invalid command-link header was read.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [23:22]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     -
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Reserved,
     <span class="documents-archterm">
      RAZ/WI
     </span>
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [21]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     STRINEARLYTERM
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Stream interface error because the AXI-Stream In interface finished earlier then AXI-Stream Out.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [20]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     STRINOVERRUN
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Stream interface error because AXI5-Write interface finished while AXI-Stream In is still busy or the Write-FIFO is not empty (and Stream In was used).
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [19]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     STRINTSTRBERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Stream interface error because of invalid tstrb detected on the AXI-Stream In interface.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [18]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     AXIRDPOISERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus error because of AXI read poison detected.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     [17]
    </p>
   </td>
   <td class="documents-nocellnorowborder" colspan="1" rowspan="1">
    <p>
     AXIWRRESPERR
    </p>
   </td>
   <td class="documents-cell-norowborder" colspan="1" rowspan="1">
    <p>
     Bus error because of AXI write error response.
    </p>
   </td>
  </tr>
  <tr>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     [16]
    </p>
   </td>
   <td class="documents-row-nocellborder" colspan="1" rowspan="1">
    <p>
     AXIRDRESPERR
    </p>
   </td>
   <td class="documents-cellrowborder" colspan="1" rowspan="1">
    <p>
     Bus error because of AXI read error response.
    </p>
   </td>
  </tr>
 </tbody>
</table>

### AXI5 bus errors

When a bus error is detected, the current DMA command stops immediately and the data associated with the bus error is discarded. All outstanding transactions are completed, but their data is also discarded. If BUSERR flag is set, at least one of AXIRDRESPERR, AXIWRRESPERR or AXIRDPOISERR is also set in the CH<x>\_ERRINFO register to indicate the source of the bus error condition.

### Configuration errors

Configuration errors are checked for before data transfer execution. No bus transfers are initiated when a configuration error is detected.

The three possible sources of configuration errors are:

- Invalid command link header (LINKHDRERR) - all bits are Read-As-Zero.
- Illegal field value set in a configuration register (REGVALERR).
- Incompatible settings are present in the configuration registers (CFGCONFLERR).

Illegal field value errors
:   The causes of illegal field value error (REGVALERR) are:

    - TRANSIZE field is greater than bus data width.
    - Trigger selector (SRCTRIGINSEL, DESTRIGINSEL, TRIGOUTSEL) value is out of valid range.

Incompatible setting errors
:   The reasons for conflicting configuration settings (CFGCONFLERR) are:

    - The trigger-in configuration conflicts with the configured transfer mode (XTYPE / YTYPE or stream settings).
    - Templated transfer is configured in an unsupported transfer mode.
    - AXI-Stream interface is enabled with an unsupported transfer mode.

    See [Configuration](/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Configuration?lang=en "The DMA-350 can be set up through its configuration registers. These registers are divided into several frames. Each register frame occupies a 256 byte address space.") for detailed conditions on incompatible settings.

### Trigger in/out selection errors

These errors could occur during the trigger allocation state when the selected trigger port or channel is not available at the clock cycle of selection. The command execution stops after the failed trigger allocation, therefore no bus transfers are initiated. The possible reasons for unavailable trigger port or channel are:

- The selected trigger port is already in use by another channel when external trigger is configured.
- The selected channel is already connected to another channel when internal trigger is configured.
- The same trigger is selected for both source and destination sides.

### AXI-Stream interface error

When an error condition is detected related to the Stream interfaces, the ongoing DMA command is stopped and the STREAMERR field is set. If STREAMERR flag is set, at least one of STRINTSTRBERR, STRINOVERRUN or STRINEARLYTERM is also set in the CH<x>\_ERRINFO register to indicate the source of the Stream interface error condition.

The possible causes for Stream interface error are:

- Stream In tstrb error (STRINTSTRBERR). This indicates that an invalid tstrb attribute is detected.
- Stream overrun error (STRINOVERRUN). This occurs when no more AXI writes are left according to DESXSIZE, but the incoming AXI-Stream has not been terminated with a tlast signal. The channel operation is stopped if this condition is detected, and the signal str\_in\_<x>\_flush is asserted on the AXI Stream-IN interface to indicate discarding of the remaining inbound data.
- Early Stream In termination (STRINEARLYTERM). If the Stream In interface finishes earlier than the Stream Out interface, this flag is set.
