# ​0x006D, STREX_PASS_SPEC, Exclusive operation speculatively executed, Store-Exclusive pass

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006D--STREX-PASS-SPEC--Exclusive-operation-speculatively-executed--Store-Exclusive-pass>

##### `0x006D`, STREX\_PASS\_SPEC, Exclusive operation speculatively executed, Store-Exclusive pass

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) Store-Exclusive instruction counted by [STREX\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x006F--STREX-SPEC--Exclusive-operation-speculatively-executed--Store-Exclusive?lang=en#event_strex_spec) that completed a write.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
