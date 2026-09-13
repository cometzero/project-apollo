# ​0x80BD, SVE_LDFF_FAULT_SPEC, Operation speculatively executed, SVE first-fault load which set FFR bit to 0

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80BD--SVE-LDFF-FAULT-SPEC--Operation-speculatively-executed--SVE-first-fault-load-which-set-FFR-bit-to-0>

##### `0x80BD`, SVE\_LDFF\_FAULT\_SPEC, Operation speculatively executed, SVE first-fault load which set FFR bit to 0

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) counted by [SVE\_LDFF\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80BC--SVE-LDFF-SPEC--Operation-speculatively-executed--SVE-first-fault-load?lang=en#event_sve_ldff_spec) due to an SVE First-fault or Non-fault load instruction that writes 0 to at least one bit in FFR.
