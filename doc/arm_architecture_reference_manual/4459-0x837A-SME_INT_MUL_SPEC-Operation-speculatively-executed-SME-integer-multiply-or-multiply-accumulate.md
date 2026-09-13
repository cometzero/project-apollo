# ​0x837A, SME_INT_MUL_SPEC, Operation speculatively executed, SME integer multiply or multiply-accumulate

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x837A--SME-INT-MUL-SPEC--Operation-speculatively-executed--SME-integer-multiply-or-multiply-accumulate>

##### `0x837A`, SME\_INT\_MUL\_SPEC, Operation speculatively executed, SME integer multiply or multiply-accumulate

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer multiply, multiply-add, or multiply-subtract operation counted by [SE\_INT\_MUL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x837B--SE-INT-MUL-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-SIMD-integer-multiply-or-multiply-accumulate?lang=en#event_se_int_mul_spec) due to any of the following instructions:

- SME2: SMLAL, SMLALL, SMLSL, SMLSLL, SUMLALL, UMLAL, UMLALL, UMLSL, UMLSLL, or USMLALL.
