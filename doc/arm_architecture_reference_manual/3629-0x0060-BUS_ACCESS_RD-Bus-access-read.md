# ​0x0060, BUS_ACCESS_RD, Bus access, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0060--BUS-ACCESS-RD--Bus-access--read>

##### `0x0060`, BUS\_ACCESS\_RD, Bus access, read

The counter counts each access counted by [BUS\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0019--BUS-ACCESS--Bus-access?lang=en#event_bus_access) that is a [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
