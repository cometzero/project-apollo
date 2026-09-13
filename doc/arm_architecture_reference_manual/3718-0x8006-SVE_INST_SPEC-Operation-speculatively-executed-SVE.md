# ​0x8006, SVE_INST_SPEC, Operation speculatively executed, SVE

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8006--SVE-INST-SPEC--Operation-speculatively-executed--SVE>

##### `0x8006`, SVE\_INST\_SPEC, Operation speculatively executed, SVE

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that is classified as an SVE operation.

An SVE operation is any operation due to an instruction that operates on the SVE scalable vector and predicate registers that is not any of the following:

- When FEAT\_SME is implemented, an operation counted by [SME\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835C--SME-SPEC--Operation-speculatively-executed--SME-data-processing?lang=en#event_sme_spec) as an SME operation.

It is IMPLEMENTATION DEFINED whether the counter counts operations due to non-SIMD instructions.

Operations due to instructions defined by FEAT\_SME which involve the SVE registers but do not involve any ZA or ZT registers are counted as SVE operations.
