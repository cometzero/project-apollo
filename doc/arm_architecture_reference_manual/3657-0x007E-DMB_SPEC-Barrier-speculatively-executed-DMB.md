# ​0x007E, DMB_SPEC, Barrier speculatively executed, DMB

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x007E--DMB-SPEC--Barrier-speculatively-executed--DMB>

##### `0x007E`, DMB\_SPEC, Barrier speculatively executed, DMB

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) data memory barrier instruction.

This includes the `CP15DSB` instruction.

This does not include the implied barrier operations of load/store operations with release consistency semantics.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
