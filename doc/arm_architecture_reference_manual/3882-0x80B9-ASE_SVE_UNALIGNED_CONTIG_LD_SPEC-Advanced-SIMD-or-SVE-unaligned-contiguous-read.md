# ​0x80B9, ASE_SVE_UNALIGNED_CONTIG_LD_SPEC, Advanced SIMD or SVE unaligned contiguous read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B9--ASE-SVE-UNALIGNED-CONTIG-LD-SPEC--Advanced-SIMD-or-SVE-unaligned-contiguous-read>

##### `0x80B9`, ASE\_SVE\_UNALIGNED\_CONTIG\_LD\_SPEC, Advanced SIMD or SVE unaligned contiguous read

The counter counts each unaligned memory access counted by [ASE\_SVE\_UNALIGNED\_CONTIG\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B8--ASE-SVE-UNALIGNED-CONTIG-LDST-SPEC--Advanced-SIMD-or-SVE-unaligned-contiguous-access?lang=en#event_ase_sve_unaligned_contig_ldst_spec) due to an A64 Advanced SIMD or SVE load instruction.

The unaligned access is counted even if it is subsequently converted into multiple aligned accesses.

It is IMPLEMENTATION DEFINED which unaligned contiguous Advanced SIMD load operations are counted in AArch32 state.
