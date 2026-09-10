# DMACH<n> description

Source: <https://developer.arm.com/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description>

### DMACH<n> description

DMA Channel Register Frame.

For an overview of the frame, and a list of constraints that apply to this block, see [DMACH<n> summary](/documentation/102482/0000/Programmers-model/Register-summary/DMACH-n--summary?lang=en "DMA Channel Register Frame.").

- **[CH\_CMD](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-CMD?lang=en)**
   The Channel DMA Command register allows the SW to control the operation of a DMA command.
- **[CH\_STATUS](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-STATUS?lang=en)**
   The Channel Status register shows the internal status of the DMA command and also reports interrupts about internal events.
- **[CH\_INTREN](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-INTREN?lang=en)**
   The Channel Interrupt Enable register can enable the interrupt generation for internal events.
- **[CH\_CTRL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-CTRL?lang=en)**
   The Channel Control register can be used to configure the type of the transfers and the resources needed by the currently executed DMA command. It also defines how the command shall behave when the command is complete.
- **[CH\_SRCADDR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCADDR?lang=en)**
   The Channel Source Address register defines the 32-bit base address of the command to read the data from. When the register is read during the execution of the command it shows an approximate hint at the actual address the DMA channel is going to read from.
- **[CH\_SRCADDRHI](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCADDRHI?lang=en)**
   The Channel Source Address Register High Bits [63:32] defines the upper 32 bits of the read address if more than 32-bit addressing is used in the system. When the register is read during the execution of the command it shows an approximate hint at the actual address the DMA channel is going to read from.
- **[CH\_DESADDR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESADDR?lang=en)**
   The Channel Destination Address register defines the 32-bit base address of the command to write the data to. When the register is read during the execution of the command it shows an approximate hint at the actual address the DMA channel is going to write to.
- **[CH\_DESADDRHI](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESADDRHI?lang=en)**
   The Channel Destination Address Register, High Bits [63:32], defines the upper 32 bits of the write address if more than 32-bit addressing is used in the system. When the register is read during the execution of the command it shows an approximate hint at the actual address the DMA channel is going to write to.
- **[CH\_XSIZE](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XSIZE?lang=en)**
   The Channel X Dimension Size Register, Lower Bits [15:0] register defines the number of data units copied during the DMA command up to 16 bits in the X dimension. The source and destination size of the command may be different for some transfer types. When read during the execution of the DMA command, the register shows an approximate hint of the remaining number of lines in both read and write directions.
- **[CH\_XSIZEHI](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XSIZEHI?lang=en)**
   The Channel X Dimension Size Register, High Bits [31:16] defines the number of data units copied during the DMA command up to 32 bits in the X dimension. The source and destination size of the command may be different for some transfer types. When read during the execution of the DMA command, the register shows an approximate hint of the remaining number of lines in both read and write directions.
- **[CH\_SRCTRANSCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTRANSCFG?lang=en)**
   The Channel Source Transfer Configuration register provides transfer attribute settings in the read direction of the DMA command.
- **[CH\_DESTRANSCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTRANSCFG?lang=en)**
   The Channel Destination Transfer Configuration register provides transfer attribute settings in the write direction of the DMA command.
- **[CH\_XADDRINC](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-XADDRINC?lang=en)**
   The Channel X Dimension Address Increment register sets the increment values used to update the source and destination addresses after each transferred data unit.
- **[CH\_YADDRSTRIDE](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-YADDRSTRIDE?lang=en)**
   The Channel Y Dimension Address Stride register sets the increment values used to update the source and destination line base addresses after each line is transferred.
- **[CH\_FILLVAL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-FILLVAL?lang=en)**
   The Channel Fill Pattern Value register provides a predefined value to be used to fill the remaining part of the destination memory area when the source side of the command is finished.
- **[CH\_YSIZE](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-YSIZE?lang=en)**
   The Channel Y Dimensions Size register defines the number of lines copied during the DMA command up to 16 bits in the Y dimension. The read and write size of the command may be different for some transfer types. When read during the execution of the DMA command, the register shows an approximate hint of the remaining number of lines in both read and write directions.
- **[CH\_TMPLTCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-TMPLTCFG?lang=en)**
   The Channel Template Configuration register provides configuration settings when using template pattern based copy operations.
- **[CH\_SRCTMPLT](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTMPLT?lang=en)**
   The Channel Source Template Pattern register sets the template pattern used for reading the source memory area.
- **[CH\_DESTMPLT](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTMPLT?lang=en)**
   The Channel Destination Template Pattern register sets the template pattern used for writing the destination memory area.
- **[CH\_SRCTRIGINCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-SRCTRIGINCFG?lang=en)**
   The Channel Source Trigger In Configuration register provides configuration settings when using source side trigger input for the current DMA command.
- **[CH\_DESTRIGINCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-DESTRIGINCFG?lang=en)**
   The Channel Destination Trigger In Configuration register provides configuration settings when using destination side trigger input for the current DMA command.
- **[CH\_TRIGOUTCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-TRIGOUTCFG?lang=en)**
   The Channel Trigger Out Configuration register provides configuration settings when using trigger output for the current DMA command.
- **[CH\_GPOEN0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOEN0?lang=en)**
   The Channel GPO Driving Enable register 0 enables which GPO ports are enabled to change at the beginning of current DMA command. GPO ports from bit 0 to 31 can be enabled by this register if the port is available to this channel.
- **[CH\_GPOVAL0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOVAL0?lang=en)**
   The Channel GPO Value register 0 sets the value to be driven on the GPO ports that are enabled at the beginning of current DMA command. The value of the GPO ports from bit 0 to 31 can be adjusted by this register if the port is available to this channel.
- **[CH\_STREAMINTCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-STREAMINTCFG?lang=en)**
   The Channel Stream Interface Configuration register provides configuration settings for the stream interface used by the current DMA command.
- **[CH\_LINKATTR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKATTR?lang=en)**
   The Channel Link Address Memory Attributes register provides transfer attribute settings for the command link related read transfers. The security and privilege attributes cannot be adjusted, they match the attributes of the channel.
- **[CH\_AUTOCFG](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-AUTOCFG?lang=en)**
   The Channel Automatic Command Restart Configuration register configures the automatic restart behavior of the currently running command.
- **[CH\_LINKADDR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKADDR?lang=en)**
   The Channel Link Address register sets the 32-bit address of the next element in a command link. When the command execution is finished and this register is set then the DMA channel starts loading the next command from this address.
- **[CH\_LINKADDRHI](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-LINKADDRHI?lang=en)**
   The Channel Link Address Register, High Bits [63:32] sets the upper address bits of the next element in a command link.
- **[CH\_GPOREAD0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-GPOREAD0?lang=en)**
   The Channel GPO Read Value register 0 shows the current value of the GPO ports from bit 0 to 31 that are available to this channel.
- **[CH\_WRKREGPTR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-WRKREGPTR?lang=en)**
   The Channel Working Register Pointer register can be used to select an internal work register of the DMA channel that is visible in the CH\_WRKREGVAL register.
- **[CH\_WRKREGVAL](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-WRKREGVAL?lang=en)**
   The Channel - Working Register Value register shows the internal value of a work register of the DMA channel selected by the CH\_WRKREGPTR register.
- **[CH\_ERRINFO](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-ERRINFO?lang=en)**
   The Channel Error Information register provides information about internal errors encountered during command execution by the DMA channel.
- **[CH\_IIDR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-IIDR?lang=en)**
   The Channel Implementation Identification register provides information about the revision of the product implementing the DMA channel.
- **[CH\_AIDR](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-AIDR?lang=en)**
   The Channel Architecture Identification register provides information about the architecture version supported by the DMA channel.
- **[CH\_ISSUECAP](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-ISSUECAP?lang=en)**
   Used for setting issuing capability threshold.
- **[CH\_BUILDCFG0](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-BUILDCFG0?lang=en)**
   The Channel Build Configuration and Capability register 0 contains the configuration parameters and capabilities of the DMA channel.
- **[CH\_BUILDCFG1](/documentation/102482/0000/Programmers-model/Register-descriptions/DMACH-n--description/CH-BUILDCFG1?lang=en)**
   The Channel Build Configuration and Capability register 1 contains the configuration parameters and capabilities of the DMA channel.
