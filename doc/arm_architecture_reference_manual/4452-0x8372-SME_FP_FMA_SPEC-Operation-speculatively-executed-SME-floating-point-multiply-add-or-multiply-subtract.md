# ​0x8372, SME_FP_FMA_SPEC, Operation speculatively executed, SME floating-point multiply-add or multiply-subtract

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8372--SME-FP-FMA-SPEC--Operation-speculatively-executed--SME-floating-point-multiply-add-or-multiply-subtract>

##### `0x8372`, SME\_FP\_FMA\_SPEC, Operation speculatively executed, SME floating-point multiply-add or multiply-subtract

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point multiply-add, multiply-add long, multiply-subtract, or multiply-subtract long operation counted by [SE\_FP\_FMA\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8373--SE-FP-FMA-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-floating-point-multiply-add-or-multiply-subtract?lang=en#event_se_fp_fma_spec) due to any of the following instructions:

- SME2: BFMLA, BFMLAL, BFMLS, BFMLSL, FMLA, FMLAL, FMLALL, FMLS, or FMLSL.
