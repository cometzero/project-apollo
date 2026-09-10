# Loading commands

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/Command-linking/Loading-commands>

### Loading commands

The command linking feature loads commands from the system memory using the same AXI bus manager interfaces that are used for data transferring.

### Command descriptor fetch attributes

The same AXI ID is used by the channels for command fetching as for the data payloads.

The command is fetched from the memory with AXI burst reads with TRANSIZE parameter set as the value of the DATA\_WIDTH parameter and the \*MAXBURSTLEN field is set to the maximum value.

The command link read uses the security and privilege state of the channel regardless of the transfer properties set in the CH<x>\_SRCTRANSCFG / CH<x>\_DESTRANSCFG registers. As a result, a Non-secure channel can only load Non-secure commands and a Secure channel can only load Secure commands.

Command link reads are distinguished on the AXI bus from data transfers with arprot\_m<x>[2] set to 1 (instruction access). An extra User signal, arcmdlink\_m<x>, is also added on the AR-channels to indicate that the read belongs to a command link fetch.

### Updating configuration registers

The header word is the first word that is read as part of the command link fetch. The consecutive reads contain the new values of the configuration registers that are updated. The register values are updated in the order as they are received.
