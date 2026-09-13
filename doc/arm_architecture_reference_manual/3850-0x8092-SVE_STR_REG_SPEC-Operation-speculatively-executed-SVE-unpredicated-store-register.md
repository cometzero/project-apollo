# ​0x8092, SVE_STR_REG_SPEC, Operation speculatively executed, SVE unpredicated store register

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8092--SVE-STR-REG-SPEC--Operation-speculatively-executed--SVE-unpredicated-store-register>

##### `0x8092`, SVE\_STR\_REG\_SPEC, Operation speculatively executed, SVE unpredicated store register

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that writes to memory counted by [SVE\_LDST\_REG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8090--SVE-LDST-REG-SPEC--Operation-speculatively-executed--SVE-unpredicated-load-or-store-register?lang=en#event_sve_ldst_reg_spec) due to any of the following instructions:

- SVE: STR.
