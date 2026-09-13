# ​0x001B, INST_SPEC, Operation speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001B--INST-SPEC--Operation-speculatively-executed>

##### `0x001B`, INST\_SPEC, Operation speculatively executed

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation.

This includes operations that are subsequently not architecturally executed.

PMCEID0\_EL0[27] reads as 1 if this event is implemented and 0 otherwise.
