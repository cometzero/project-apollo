# ​0x0065, BUS_ACCESS_PERIPH, Bus access, peripheral

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0065--BUS-ACCESS-PERIPH--Bus-access--peripheral>

##### `0x0065`, BUS\_ACCESS\_PERIPH, Bus access, peripheral

The counter counts each access counted by [BUS\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0019--BUS-ACCESS--Bus-access?lang=en#event_bus_access) that is not counted by [BUS\_ACCESS\_NORMAL](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0064--BUS-ACCESS-NORMAL--Bus-access--normal?lang=en#event_bus_access_normal).

For example, the counter counts accesses to Device memory.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
