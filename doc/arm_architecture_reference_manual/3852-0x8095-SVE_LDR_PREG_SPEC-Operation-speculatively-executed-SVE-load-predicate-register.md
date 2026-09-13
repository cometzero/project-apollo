# ​0x8095, SVE_LDR_PREG_SPEC, Operation speculatively executed, SVE load predicate register

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8095--SVE-LDR-PREG-SPEC--Operation-speculatively-executed--SVE-load-predicate-register>

##### `0x8095`, SVE\_LDR\_PREG\_SPEC, Operation speculatively executed, SVE load predicate register

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [SVE\_LDST\_PREG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8094--SVE-LDST-PREG-SPEC--Operation-speculatively-executed--SVE-load-or-store-predicate-register?lang=en#event_sve_ldst_preg_spec) due to any of the following instructions:

- SVE: LDR (predicate).
