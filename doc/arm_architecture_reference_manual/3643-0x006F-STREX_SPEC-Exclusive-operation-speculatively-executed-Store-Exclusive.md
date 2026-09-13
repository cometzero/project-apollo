# ​0x006F, STREX_SPEC, Exclusive operation speculatively executed, Store-Exclusive

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006F--STREX-SPEC--Exclusive-operation-speculatively-executed--Store-Exclusive>

##### `0x006F`, STREX\_SPEC, Exclusive operation speculatively executed, Store-Exclusive

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) Store-Exclusive instruction.

The definition of [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) is IMPLEMENTATION DEFINED but it must be the same as for the [LDREX\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006C--LDREX-SPEC--Exclusive-operation-speculatively-executed--Load-Exclusive?lang=en#event_ldrex_spec) event.

Arm recommends that this event is implemented if it is not possible to implement the exclusive operation [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece), Store-Exclusive pass, and exclusive operation [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece), Store-Exclusive fail, events with the same degree of speculation as the [LDREX\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006C--LDREX-SPEC--Exclusive-operation-speculatively-executed--Load-Exclusive?lang=en#event_ldrex_spec) event.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
