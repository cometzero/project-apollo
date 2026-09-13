# ​0x8085, ASE_SVE_LD_SPEC, Operation speculatively executed, Advanced SIMD or SVE load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8085--ASE-SVE-LD-SPEC--Operation-speculatively-executed--Advanced-SIMD-or-SVE-load>

##### `0x8085`, ASE\_SVE\_LD\_SPEC, Operation speculatively executed, Advanced SIMD or SVE load

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [ASE\_SVE\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8084--ASE-SVE-LDST-SPEC--Operation-speculatively-executed--Advanced-SIMD-or-SVE-load-or-store?lang=en#event_ase_sve_ldst_spec) due to an A64 Advanced SIMD or SVE load instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD load operations are counted in AArch32 state.
