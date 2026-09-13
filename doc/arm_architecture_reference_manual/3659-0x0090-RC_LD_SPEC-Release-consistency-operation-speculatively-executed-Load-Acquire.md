# ​0x0090, RC_LD_SPEC, Release consistency operation speculatively executed, Load-Acquire

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0090--RC-LD-SPEC--Release-consistency-operation-speculatively-executed--Load-Acquire>

##### `0x0090`, RC\_LD\_SPEC, Release consistency operation speculatively executed, Load-Acquire

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) with acquire or acquirepc semantics.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
