# ​0x805B, ASE_SVE_NONFP_SPEC, Non-floating-point operation speculatively executed, Advanced SIMD or SVE

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x805B--ASE-SVE-NONFP-SPEC--Non-floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE>

##### `0x805B`, ASE\_SVE\_NONFP\_SPEC, Non-floating-point operation speculatively executed, Advanced SIMD or SVE

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) non-floating-point operation counted by [NONFP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8058--NONFP-SPEC--Non-floating-point-operation-speculatively-executed?lang=en#event_nonfp_spec) due to an A64 Advanced SIMD or SVE instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD non-floating-point data-processing operations are counted in AArch32 state.
