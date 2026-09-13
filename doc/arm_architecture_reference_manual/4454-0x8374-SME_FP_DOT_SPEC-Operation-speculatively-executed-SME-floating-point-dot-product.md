# ​0x8374, SME_FP_DOT_SPEC, Operation speculatively executed, SME floating-point dot product

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8374--SME-FP-DOT-SPEC--Operation-speculatively-executed--SME-floating-point-dot-product>

##### `0x8374`, SME\_FP\_DOT\_SPEC, Operation speculatively executed, SME floating-point dot product

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point dot product operation counted by [SE\_FP\_DOT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8375--SE-FP-DOT-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-floating-point-dot-product?lang=en#event_se_fp_dot_spec) due to any of the following instructions:

- SME2: BFDOT, BFVDOT, FDOT, FVDOT, FVDOTB, or FVDOTT.
