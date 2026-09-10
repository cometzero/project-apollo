# Automatic boot interface

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/Configuration-interface/Automatic-boot-interface>

### Automatic boot interface

The boot interface consists of the following signals:

- boot\_en - to enable automatic booting,
- boot\_addr - address of boot command descriptor,
- boot\_memattr - AXI memory attributes to be used during fetching the boot command descriptor,
- boot\_shareattr - AXI memory Shareability attributes to be used during fetching the boot command descriptor.

Assertion of the boot\_en indicates that automatic booting is enabled and the other signals are valid. If boot\_en is not asserted, automatic booting is disabled and the other boot signals are ignored. All boot signals must be stable when deasserting the reset and remain stable until fetching of the boot command is started.

For more detail on automatic booting, see [Automatic boot feature](/documentation/102482/0000/DMAC-operation/Command-linking/Automatic-boot-feature?lang=en "The DMA unit implements an automatic boot feature called autoboot to speed up the bootup of the system. The autoboot can load the first DMA command into channel 0 and start executing it. Autoboot is implemented with the command-link feature and it can be configured with dedicated input signals.").
