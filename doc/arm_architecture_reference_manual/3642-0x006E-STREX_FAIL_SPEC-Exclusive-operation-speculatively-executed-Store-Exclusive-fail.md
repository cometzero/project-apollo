# ​0x006E, STREX_FAIL_SPEC, Exclusive operation speculatively executed, Store-Exclusive fail

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006E--STREX-FAIL-SPEC--Exclusive-operation-speculatively-executed--Store-Exclusive-fail>

##### `0x006E`, STREX\_FAIL\_SPEC, Exclusive operation speculatively executed, Store-Exclusive fail

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) Store-Exclusive instruction counted by [STREX\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006F--STREX-SPEC--Exclusive-operation-speculatively-executed--Store-Exclusive?lang=en#event_strex_spec) that fails to complete a write.

It is within the IMPLEMENTATION DEFINED definition of [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) whether this includes conditional instructions that fail the condition code check.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
