# ​0x8392, SME_ST_REG_SPEC, SME unpredicated store

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8392--SME-ST-REG-SPEC--SME-unpredicated-store>

##### `0x8392`, SME\_ST\_REG\_SPEC, SME unpredicated store

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that writes to memory counted by [SME\_LDST\_REG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8390--SME-LDST-REG-SPEC--SME-unpredicated-load-store?lang=en#event_sme_ldst_reg_spec) that was due to an unpredicated instruction targeting the ZA array or ZT register.

That is, due to any of the following instructions:

- SME2: STR.
