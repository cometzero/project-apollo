# ​0x838D, SME_LD_ZTREG_SPEC, SME ZT unpredicated load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x838D--SME-LD-ZTREG-SPEC--SME-ZT-unpredicated-load>

##### `0x838D`, SME\_LD\_ZTREG\_SPEC, SME ZT unpredicated load

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [SME\_LDST\_ZTREG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x838C--SME-LDST-ZTREG-SPEC--SME-ZT-unpredicated-load-store?lang=en#event_sme_ldst_ztreg_spec) that was due to an unpredicated instruction targeting the ZT register.

That is, due to any of the following instructions:

- SME2: LDR (table).
