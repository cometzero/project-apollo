# ​0x80B6, ASE_SVE_UNALIGNED_ST_SPEC, Advanced SIMD or SVE unaligned write

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B6--ASE-SVE-UNALIGNED-ST-SPEC--Advanced-SIMD-or-SVE-unaligned-write>

##### `0x80B6`, ASE\_SVE\_UNALIGNED\_ST\_SPEC, Advanced SIMD or SVE unaligned write

The counter counts each unaligned memory access counted by [ASE\_SVE\_UNALIGNED\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B4--ASE-SVE-UNALIGNED-LDST-SPEC--Advanced-SIMD-or-SVE-unaligned-access?lang=en#event_ase_sve_unaligned_ldst_spec) due to an A64 Advanced SIMD or SVE store instruction.

The unaligned access is counted even if it is subsequently converted into multiple aligned accesses.

It is IMPLEMENTATION DEFINED which unaligned Advanced SIMD store operations are counted in AArch32 state.
