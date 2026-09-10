# Initialization

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/Initialization>

### Initialization

The DMAC must be configured to set the security and privilege attributes for each channel and their attached resources before setting the channels for memory transfers. When the configuration is complete, the channel configuration registers are protected against malicious accesses. The security configuration can be locked until the next reset of the DMAC to further protect the security settings. Privilege settings of a channel can be adjusted when the channel is in IDLE. The register settings are automatically cleared when the security or privilege settings of a channel change.

> ### Note
>
> We recommend that the security or privilege change is done with a sequence of writing and reading back the desired new state to assure the success of the change.

The DMAC checks the boot\_en port after reset. If automatic booting is turned on, the DMAC sets the boot address as the first link address for channel 0 and enables the channel before any APB4 configuration can occur. When security is enabled for the DMAC, the channel 0 is set to be Secure as all other channels so only Secure commands can be fetched from the memory.
