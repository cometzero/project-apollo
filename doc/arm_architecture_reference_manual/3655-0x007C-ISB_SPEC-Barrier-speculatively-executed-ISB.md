# ​0x007C, ISB_SPEC, Barrier speculatively executed, ISB

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x007C--ISB-SPEC--Barrier-speculatively-executed--ISB>

##### `0x007C`, ISB\_SPEC, Barrier speculatively executed, ISB

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) Instruction Synchronization Barrier instruction.

This includes the `CP15ISB` instruction.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
