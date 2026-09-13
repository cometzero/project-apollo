# ​0x8091, SVE_LDR_REG_SPEC, Operation speculatively executed, SVE unpredicated load register

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8091--SVE-LDR-REG-SPEC--Operation-speculatively-executed--SVE-unpredicated-load-register>

##### `0x8091`, SVE\_LDR\_REG\_SPEC, Operation speculatively executed, SVE unpredicated load register

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [SVE\_LDST\_REG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8090--SVE-LDST-REG-SPEC--Operation-speculatively-executed--SVE-unpredicated-load-or-store-register?lang=en#event_sve_ldst_reg_spec) due to any of the following instructions:

- SVE: LDR.
