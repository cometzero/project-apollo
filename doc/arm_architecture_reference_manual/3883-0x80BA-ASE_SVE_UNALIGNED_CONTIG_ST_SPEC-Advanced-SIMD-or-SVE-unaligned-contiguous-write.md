# ​0x80BA, ASE_SVE_UNALIGNED_CONTIG_ST_SPEC, Advanced SIMD or SVE unaligned contiguous write

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80BA--ASE-SVE-UNALIGNED-CONTIG-ST-SPEC--Advanced-SIMD-or-SVE-unaligned-contiguous-write>

##### `0x80BA`, ASE\_SVE\_UNALIGNED\_CONTIG\_ST\_SPEC, Advanced SIMD or SVE unaligned contiguous write

The counter counts each unaligned memory access counted by [ASE\_SVE\_UNALIGNED\_CONTIG\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B8--ASE-SVE-UNALIGNED-CONTIG-LDST-SPEC--Advanced-SIMD-or-SVE-unaligned-contiguous-access?lang=en#event_ase_sve_unaligned_contig_ldst_spec) due to a A64 Advanced SIMD or SVE store instruction.

The unaligned access is counted even if it is subsequently converted into multiple aligned accesses.

It is IMPLEMENTATION DEFINED which unaligned contiguous Advanced SIMD store operations are counted in AArch32 state.
