# ​0x8376, SME_FP_MOPA_SPEC, Operation speculatively executed, SME floating-point outer product and accumulate, or outer product and subtract

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8376--SME-FP-MOPA-SPEC--Operation-speculatively-executed--SME-floating-point-outer-product-and-accumulate--or-outer-product-and-subtract>

##### `0x8376`, SME\_FP\_MOPA\_SPEC, Operation speculatively executed, SME floating-point outer product and accumulate, or outer product and subtract

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point outer product and accumulate, or outer product and subtract operation counted by [SE\_FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8353--SE-FP-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-floating-point--data-processing?lang=en#event_se_fp_spec) due to any of the following instructions:

- SME2: BFMOPA, BFMOPS, FMOPA, or FMOPS.
