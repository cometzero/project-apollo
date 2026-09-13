# ​0x4021, LD_ALIGN_LAT, Load with additional latency from alignment

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4021--LD-ALIGN-LAT--Load-with-additional-latency-from-alignment>

##### `0x4021`, LD\_ALIGN\_LAT, Load with additional latency from alignment

The counter counts each [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) counted by [LDST\_ALIGN\_LAT](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4020--LDST-ALIGN-LAT--Access-with-additional-latency-from-alignment?lang=en#event_ldst_align_lat).

PMCEID1\_EL0[33] reads as 1 if this event is implemented and 0 otherwise.
