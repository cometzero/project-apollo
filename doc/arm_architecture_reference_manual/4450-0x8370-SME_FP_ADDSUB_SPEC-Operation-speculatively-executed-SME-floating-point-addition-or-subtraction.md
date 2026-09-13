# ​0x8370, SME_FP_ADDSUB_SPEC, Operation speculatively executed, SME floating-point addition or subtraction

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8370--SME-FP-ADDSUB-SPEC--Operation-speculatively-executed--SME-floating-point-addition-or-subtraction>

##### `0x8370`, SME\_FP\_ADDSUB\_SPEC, Operation speculatively executed, SME floating-point addition or subtraction

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point addition or subtraction operation counted by [SE\_FP\_ADDSUB\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8371--SE-FP-ADDSUB-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-floating-point-addition-or-subtraction?lang=en#event_se_fp_addsub_spec) due to any of the following instructions:

- SME2: BFADD, BFSUB, FADD, or FSUB.
