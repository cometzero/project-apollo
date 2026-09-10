# Transfer attributes

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-interfaces/AXI5-manager-interfaces/Transfer-attributes>

### Transfer attributes

The memory attributes of the transfers can be adjusted from SW configurable registers for each command. Security and privilege settings can be adjusted for Secure or privileged channels. Device or memory types can be selected for read and write sides separately. Cacheability and Shareability values can also be set to match the settings of the memory location the DMA transfer is targeting. These settings must match the values defined in other components of the system and can affect the performance of each transfer.

Command link related reads are always sent out as instruction type transfers, that is, arprot[2] is driven 1. Command link accesses inherit the security and privilege settings of the channel.
