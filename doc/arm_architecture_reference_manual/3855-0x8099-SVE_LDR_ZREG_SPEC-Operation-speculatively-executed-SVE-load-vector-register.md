# ​0x8099, SVE_LDR_ZREG_SPEC, Operation speculatively executed, SVE load vector register

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8099--SVE-LDR-ZREG-SPEC--Operation-speculatively-executed--SVE-load-vector-register>

##### `0x8099`, SVE\_LDR\_ZREG\_SPEC, Operation speculatively executed, SVE load vector register

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [SVE\_LDST\_ZREG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8098--SVE-LDST-ZREG-SPEC--Operation-speculatively-executed--SVE-load-or-store-vector-register?lang=en#event_sve_ldst_zreg_spec) due to any of the following instructions:

- SVE: LDR (vector).
