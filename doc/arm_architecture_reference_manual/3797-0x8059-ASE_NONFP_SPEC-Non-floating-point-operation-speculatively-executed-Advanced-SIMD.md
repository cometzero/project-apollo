# ​0x8059, ASE_NONFP_SPEC, Non-floating-point operation speculatively executed, Advanced SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8059--ASE-NONFP-SPEC--Non-floating-point-operation-speculatively-executed--Advanced-SIMD>

##### `0x8059`, ASE\_NONFP\_SPEC, Non-floating-point operation speculatively executed, Advanced SIMD

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) non-floating-point operation counted by [ASE\_SVE\_NONFP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x805B--ASE-SVE-NONFP-SPEC--Non-floating-point-operation-speculatively-executed--Advanced-SIMD-or-SVE?lang=en#event_ase_sve_nonfp_spec) due to an A64 Advanced SIMD instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD non-floating-point data-processing operations are counted in AArch32 state.
