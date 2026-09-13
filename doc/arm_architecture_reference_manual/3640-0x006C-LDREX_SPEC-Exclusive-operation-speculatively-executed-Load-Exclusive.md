# ​0x006C, LDREX_SPEC, Exclusive operation speculatively executed, Load-Exclusive

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006C--LDREX-SPEC--Exclusive-operation-speculatively-executed--Load-Exclusive>

##### `0x006C`, LDREX\_SPEC, Exclusive operation speculatively executed, Load-Exclusive

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) Load-Exclusive instruction.

The definition of [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) is IMPLEMENTATION DEFINED but must be the same as for the [STREX\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006F--STREX-SPEC--Exclusive-operation-speculatively-executed--Store-Exclusive?lang=en#event_strex_spec) event.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
