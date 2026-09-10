# Automatic boot feature

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/Command-linking/Automatic-boot-feature>

### Automatic boot feature

The DMA unit implements an automatic boot feature called autoboot to speed up the bootup of the system. The autoboot can load the first DMA command into channel 0 and start executing it. Autoboot is implemented with the command-link feature and it can be configured with dedicated input signals.

The boot command or commands must be prepared in memory, which may contain any DMAC configuration register value supported by command linking. This provides the possibility to set up an initial single memory-to-memory copy command or a chain of multiple commands that are executed automatically at start-up.

### Enabling the autoboot feature

The address of the boot command and some additional attributes must be configured as input signals, and the boot enable signal must be set HIGH to enable the autoboot feature. To execute an autoboot, the following signals must be set before deactivating the device reset. They must also be stable until the fetching of the boot command is started.

- boot\_en = 1’b1
- boot\_addr = <address of boot command descriptor>
- boot\_memattr = <AXI memory attributes to be used during fetching the boot command descriptor>
- boot\_shareattr = <AXI memory Shareability attributes to be used during fetching the boot command descriptor>

When Security Extension is used, DMA channel 0 starts as Secure, therefore the boot address must point to a Secure address location.

### Autoboot process

The autoboot process is initiated after the DMA-350 is released from reset and both LPI channels have entered their active state. The input signals are sampled at this point, and the process begins with writing the preconfigured boot address and attributes to Channel 0 configuration registers as an initial, empty linked-command.

After this process, the boot command referenced by boot\_addr is fetched and gets written to Channel 0 configuration registers. Finally, the DMAC executes the boot command.

Channel 0 status signals can be used to track the boot process. For example, ch\_enabled[0] is asserted throughout the boot command like any other DMA command executed on Channel 0.
