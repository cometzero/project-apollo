# ​0x0064, BUS_ACCESS_NORMAL, Bus access, normal

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0064--BUS-ACCESS-NORMAL--Bus-access--normal>

##### `0x0064`, BUS\_ACCESS\_NORMAL, Bus access, normal

The counter counts each access counted by [BUS\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0019--BUS-ACCESS--Bus-access?lang=en#event_bus_access) that is to Normal or bulk memory.

For example, the counter counts Normal, Cacheable and Normal, Non-cacheable accesses but does not count Device accesses.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
