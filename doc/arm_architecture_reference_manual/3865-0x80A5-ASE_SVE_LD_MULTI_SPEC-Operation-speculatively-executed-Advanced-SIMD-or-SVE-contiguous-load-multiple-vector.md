# ​0x80A5, ASE_SVE_LD_MULTI_SPEC, Operation speculatively executed, Advanced SIMD or SVE contiguous load multiple vector

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A5--ASE-SVE-LD-MULTI-SPEC--Operation-speculatively-executed--Advanced-SIMD-or-SVE-contiguous-load-multiple-vector>

##### `0x80A5`, ASE\_SVE\_LD\_MULTI\_SPEC, Operation speculatively executed, Advanced SIMD or SVE contiguous load multiple vector

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [ASE\_SVE\_LDST\_MULTI\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80A4--ASE-SVE-LDST-MULTI-SPEC--Operation-speculatively-executed--Advanced-SIMD-or-SVE-contiguous-load-or-store-multiple-vector?lang=en#event_ase_sve_ldst_multi_spec) due to an A64 Advanced SIMD or SVE multiple vector contiguous structure load instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD contiguous structure load operations are counted in AArch32 state.
