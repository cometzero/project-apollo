# ​0x802C, FP_MUL_SPEC, Floating-point operation speculatively executed, multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x802C--FP-MUL-SPEC--Floating-point-operation-speculatively-executed--multiply>

##### `0x802C`, FP\_MUL\_SPEC, Floating-point operation speculatively executed, multiply

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point multiply operation counted by [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec) due to any of the following A64 instructions:

- Scalar: FMUL or FMULX.
- Advanced SIMD: FMUL or FMULX.
- SVE: FMUL, FMULX, or FTSMUL.
- SVE2: BFMUL.

It is IMPLEMENTATION DEFINED which floating-point multiply operations are counted in AArch32 state.
