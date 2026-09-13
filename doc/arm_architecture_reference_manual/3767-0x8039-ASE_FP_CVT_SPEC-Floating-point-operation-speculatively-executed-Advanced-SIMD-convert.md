# ​0x8039, ASE_FP_CVT_SPEC, Floating-point operation speculatively executed, Advanced SIMD convert

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8039--ASE-FP-CVT-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-convert>

##### `0x8039`, ASE\_FP\_CVT\_SPEC, Floating-point operation speculatively executed, Advanced SIMD convert

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point convert operation counted by [ASE\_SVE\_FP\_CVT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x803B--ASE-SVE-FP-CVT-SPEC--Floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE-convert?lang=en#event_ase_sve_fp_cvt_spec) due to an A64 Advanced SIMD instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD floating-point convert operations are counted in AArch32 state.
