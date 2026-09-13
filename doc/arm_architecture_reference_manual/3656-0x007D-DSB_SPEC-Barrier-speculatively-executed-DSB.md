# ​0x007D, DSB_SPEC, Barrier speculatively executed, DSB

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x007D--DSB-SPEC--Barrier-speculatively-executed--DSB>

##### `0x007D`, DSB\_SPEC, Barrier speculatively executed, DSB

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) data synchronization and speculative load barrier instruction.

This includes the `CP15DSB`, `SSBB`, and `PSSBB` instructions.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
