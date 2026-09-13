# ​0x8389, SME_LD_ZAREG_SPEC, SME ZA unpredicated load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8389--SME-LD-ZAREG-SPEC--SME-ZA-unpredicated-load>

##### `0x8389`, SME\_LD\_ZAREG\_SPEC, SME ZA unpredicated load

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [SME\_LDST\_ZAREG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8388--SME-LDST-ZAREG-SPEC--SME-ZA-unpredicated-load-store?lang=en#event_sme_ldst_zareg_spec) that was due to an unpredicated instruction targeting the ZA array.

That is, due to any of the following instructions:

- SME2: LDR (array vector).
