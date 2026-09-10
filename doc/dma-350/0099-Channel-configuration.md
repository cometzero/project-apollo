# Channel configuration

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-power-management-and-DMAC-control/Configuration/Channel-configuration>

### Channel configuration

Each DMA channel has its own register frame which contains the channel-specific configuration registers. The configuration registers are writable only when the channel is not enabled. When the ENABLECMD bit is set in the CH<x>\_CMD register, the settings are frozen throughout the execution of the command.

To configure a command correctly, the settings written to the configuration registers must meet the following criteria:

- The register fields must contain allowed values only. To see which values are valid, see [Programmers model](/documentation/102482/0000/Programmers-model?lang=en "This section describes the functionality of the DMA-350 from a programming perspective."). All bits of reserved fields must be zeroes. Failing to meet this criteria results in REGVALERR.
- The settings must describe a command that is valid, that is, there are no conflicting parameters. Failing to meet this criteria results in CFGCONFLERR.

### Configuring a channel command

The following registers and fields must be written to set up a DMA command:

1. CH<x>\_CTRL register:

   - CHPRIO - DMA channel priority
   - TRANSIZE - Unit of data transfers
   - XTYPE / YTYPE - Type of intended data transfer
   - USE\* fields to select whether triggers / GPO / Stream interface to be used
   - DONETYPE / DONEPAUSEEN fields to control at which point of the command execution the STAT\_DONE flag is to be signaled, and if the channel is to be paused as a result.
2. Source / destination start addresses

   CH<x>\_SRCADDR and CH<x>\_SRCADDRHI define source start address, while CH<x>\_DESADDR and CH<x>\_DESADDRHI define destination start address of the transfer.
3. Source / destination sizes, Y-stride

   SRCXSIZE and SRCXSIZEHI define source XSIZE, while DESXSIZE and DESXSIZEHI define destination XSIZE parameters of the transfer. These files are located in the CH<x>\_XSIZE and CH<x>\_XSIZEHI registers.

   If a 2D transfer was selected through YTYPE, the YSIZE parameters must also be set by the SRCYSIZE and DESYSIZE fields in the CH<x>\_YSIZE register. In addition, the SRCYADDRSTRIDE / DESYADDRSTRIDE parameters must be configured in the CH<x>\_YADDRSTRIDE register for 2D transfers.
4. Source / destination address increments:

   SRCXADDRINC and DESXADDRINC define the address increments in the CH<x>\_XADDRINC register.

   These fields are encoded as two’s complement numbers, so negative and zero values are also possible to be used.
5. Source / destination bus attributes in the CH<x>\_SRCTRANSCFG / CH<x>\_DESTRANSCFG registers:

   - Security and privilege attributes (\*NONSECATTR / \*PRIVATTR)
   - Memory and Shareability attributes (\*MEMATTRLO / \*MEMATTRHI / \*SHAREATTR)
   - Maximum burst length (\*MAXBURSTLEN)
6. If the selected transfer type in XTYPE or YTYPE is ‘fill’, the fill value must be set in the CH<x>\_FILLVAL register.
7. For templated transfers, the template patterns and template sizes must be set in the CH<x>\_TMPLTCFG, CH<x>\_SRCTMPLT, and CH<x>\_DESTMPLT registers. To disable templated transfers, set the template sizes to zero.
8. If triggering is used (selected by the USESRCTRIGIN, USEDESTRIGIN or USETRIGOUT fields), the triggers must be configured for the enabled triggers.

   - For trigger inputs, the following fields must be set in the CH<x>\_SRCTRIGINCFG / CH<x>\_DESTRIGINCFG registers:

     - \*TRIGINTYPE - the type of the input trigger (SW only, external HW, or internal trigger)
     - \*TRIGINMODE - the trigger input mode (command trigger, DMAC driven flow control trigger, or peripheral driven flow control trigger)
     - \*TRIGINSEL - to select which external trigger port to be used if external HW type is selected, or which channel to be connected if internal type is selected.
     - \*TRIGINBLKSIZE - to define the trigger block size for flow control trigger modes
   - For trigger outputs, the following fields must be set in the CH<x>\_TRIGOUTCFG register:

     - TRIGOUTTYPE - the type of the output trigger (SW only, external HW, or internal trigger)
     - TRIGOUTSEL - to select which external trigger port to be used if external HW type is selected (don’t care for other types)
9. GPO value (CH<x>\_GPOVAL0) and enable mask (CH<x>\_GPOEN0) if GPO is to be used.
10. If Stream interface is to be used, the STREAMTYPE field must be configured in the CH<x>\_STREAMINTCFG register.
11. To enable auto restart, the restart counter must be set, or the infinite restart flag must be enabled:

    - Set CMDRESTARTCNT to the number of intended cycled minus one, or
    - Set CMDRESTARTINFEN to 1 to enable infinite automatic restarting of commands.
    - Select the registers to be reloaded with their initial value after each cycle by setting the REGRELOADTYPE field in the CH<x>\_CTRL register.
12. For command linking, the following fields must be set:

    - LINKADDREN must be set to 1 to enable command linking
    - LINKADDR / LINKADDRHI - to set the address of the linked-command descriptor
    - LINKMEMATTRLO / LINKMEMATTRHI / LINKSHAREATTR - to set the bus transfer attributes to be used for fetching the descriptor

If a feature is not used by the command, we recommend that the fields associated with the feature are left in the reset values.

### Empty commands

There is a subset of settings that describe a valid command, but the execution does not result in actual data transfers. Such commands, called empty commands, can be useful. For example, to initiate a linked command chain, to set a GPO value, or to synchronize with other channels using the triggering features.

An empty command is executed if the XTYPE field is explicitly set to ‘disable’ (3’b000), or when neither data reads nor data writes are configured for the AXI5 interface.

The following cases result in no data reads through the AXI5 interface:

- Explicit empty command is requested:

  ```
  XTYPE = 'disable'
  ```
- Stream to AXI mode is selected (if Stream is supported by the channel):

  ```
  USESTREAM = 1'b1 and STREAMTYPE = 'Stream in only'
  ```
- Data source is configured to AXI, but source size is set to zero:

  ```
  ( USESTREAM = 1'b0 or (USESTREAM = 1'b1 and STREAMTYPE = {'Stream in and out' or 'Stream out only'}) )
     and
  ( SRCXSIZE = 0 or (YTYPE != 'disable' and SRCYSIZE = 0) )
  ```
- AXI to AXI mode is selected, but destination size is set to zero:

  ```
  ( USESTREAM = 1'b0 or (USESTREAM = 1'b1 and STREAMTYPE = 'Stream in and out') )
     and
  ( DESXSIZE = 0 or (YTYPE != 'disable' and DESYSIZE = 0) )
  ```

The following cases result in no data writes through the AXI5 interface:

- Explicit empty command is requested:

  ```
  XTYPE = 'disable'
  ```
- AXI to stream mode is selected (if Stream is supported by the channel):

  ```
  USESTREAM = 1'b1 and STREAMTYPE = 'Stream out only'
  ```
- Data destination is configured to AXI, but destination size is set to zero:

  ```
  ( USESTREAM = 1'b0 or (USESTREAM = 1'b1 and STREAMTYPE = {'Stream in and out' or 'Stream in only'}) )
     and
  ( DESXSIZE = 0 or (XTYPE != 'disable' and DESYSIZE = 0) )
  ```
- AXI to AXI mode is selected, but there is no data producer (source size is set to zero and no Y fill mode selected for 2D commands or no X fill selected for 1D commands):

  ```
  ( USESTREAM = 1'b0 or (USESTREAM = 1'b1 and STREAMTYPE = 'Stream in and out') )
     and
  ( SRCXSIZE = 0 or (YTYPE != 'disable' and SRCYSIZE = 0) )
     and
  ( ( YTYPE != 'disable' and YTYPE != 'fill' ) or ( YTYPE = 'disable' and XTYPE != 'fill' ) )
  ```

> ### Note
>
> The recommended method for configuring an empty command intentionally is to set XTYPE to ‘disable’.

### Configuration errors because of invalid settings

The following invalid settings result in configuration errors. No data transfers are made, and the CFGERR and REGVALERR fields are set in the CH<x>\_ERRINFO register.

- TRANSIZE is set to be greater than the bus width.
- Non-existent trigger resource is selected:

  - If you configure HW trigger type (SRCTRIGINTYPE, DESTRIGINTYPE or TRIGOUTTYPE = 2’b10), SRCTRIGINSEL, DESTRIGINSEL or TRIGOUTSEL points to a HW trigger port number that is too high.
  - If you configure internal trigger type (SRCTRIGINTYPE or DESTRIGINTYPE = 2’b11), SRCTRIGINSEL, DESTRIGINSEL points to a channel number that is too high, or points to the channel itself that is being configured.
  - Configuring HW trigger type (SRCTRIGINTYPE, DESTRIGINTYPE or TRIGOUTTYPE = 2’b10), when the $product does not have HW trigger in or trigger out port.

### Configuration errors because of conflicting settings

The following settings result in configuration conflict errors. No data transfers are, and the CFGERR and CFGCONFLERR fields are set in the CH<x>\_ERRINFO register.

- Flow control trigger input modes are only supported with 1D source or destination. It means that even if a 2D transfer type is selected, the YSIZE must be 1 on the given side.

  In addition, flow control trigger modes are not supported when using the stream interface. The reason for this restriction is that block-based transfers might behave improperly when converted to stream output transfers.

  Finally, wrap transfer typed are not allowed with source flow control trigger mode. The following configuration settings are illegal:

  - Source flow control trigger input mode with 2D source:

  ```
  USESRCTRIGIN = 1'b1 and SRCTRIGINMODE = 2'b1X and XTYPE != 'disable' and YTYPE != 'disable' and SRCYSIZE > 1
  ```

  - Destination flow control trigger input mode with 2D destination:

  ```
  USEDESTRIGIN = 1'b1 and DESTRIGINMODE = 2'b1X and XTYPE != 'disable' and YTYPE != 'disable' and DESYSIZE > 1
  ```

  - Using Stream interface with source flow control trigger input mode

  ```
  USESRCTRIGIN = 1'b1 and SRCTRIGINMODE = 2'b1X and USESTREAM = 1'b1
  ```

  - Using Stream interface with destination flow control trigger input mode

  ```
  USEDESTRIGIN = 1'b1 and DESTRIGINMODE = 2'b1X and USESTREAM = 1'b1
  ```

  - Source flow control trigger input mode with wrap transfers:

  ```
  USESRCTRIGIN = 1'b1 and SRCTRIGINMODE = 2'b1X and (XTYPE == 'wrap' or YTYPE == 'wrap')
  ```
- Flow control trigger modes imply that there must be data transfer configured for the given direction. For the definitions of no AXI5 read or write configured, see the Empty commands section above.

  Therefore, the following settings are illegal:

  - Source flow control trigger input mode when no AXI5 source data:

  ```
  USESRCTRIGIN = 1'b1 and SRCTRIGINMODE = 2'b1X and No AXI5 read configured
  ```

  - Destination flow control trigger input mode when no AXI5 destination data:

  ```
  USEDESTRIGIN = 1'b1 and DESTRIGINMODE = 2'b1X and No AXI5 write configured
  ```
- The stream interface cannot work with certain transfer types. The following settings are illegal:

  ```
  USESTREAM = 1'b1
     and
  ( (XTYPE == 'wrap' and YTYPE == 'disable') or
    (XTYPE == 'continue' and YTYPE == 'wrap') or
    (XTYPE == {'wrap' or 'fill'} and YTYPE == {'wrap' or 'continue' or 'fill'})
  )
  ```
- When using the stream interface with AXI to AXI transfers and fill transfer types, there must be AXI data source. Therefore, the following settings are illegal:

  ```
  USESTREAM = 1'b1 and STREAMTYPE = 'Stream in and out'
     and
  ( (XTYPE == 'fill' and YTYPE == 'disable') or (XTYPE == 'continue' and YTYPE == 'fill') )
     and
  No AXI5 read configured
  ```
- Templated transfers are not allowed with 2D transfer types.

  ```
  YTYPE != 'disable' and (SRCTMPLTSIZE != 0 or DESTMPLTSIZE != 0)
  ```
