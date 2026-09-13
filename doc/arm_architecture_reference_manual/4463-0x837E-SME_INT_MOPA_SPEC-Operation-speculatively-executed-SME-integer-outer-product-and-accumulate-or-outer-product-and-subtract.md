# ​0x837E, SME_INT_MOPA_SPEC, Operation speculatively executed, SME integer outer product and accumulate, or outer product and subtract

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x837E--SME-INT-MOPA-SPEC--Operation-speculatively-executed--SME-integer-outer-product-and-accumulate--or-outer-product-and-subtract>

##### `0x837E`, SME\_INT\_MOPA\_SPEC, Operation speculatively executed, SME integer outer product and accumulate, or outer product and subtract

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer outer product and accumulate, or outer product and subtract operation counted by [SE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8379--SE-INT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer--data-processing?lang=en#event_se_int_spec) due to any of the following instructions:

- SME2: BMOPA, BMOPS, SMOPA, SMOPS, SUMOPA (4-way), SUMOPS, UMOPA, UMOPS, USMOPA (4-way), or USMOPS.
