# ​0x80B8, ASE_SVE_UNALIGNED_CONTIG_LDST_SPEC, Advanced SIMD or SVE unaligned contiguous access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B8--ASE-SVE-UNALIGNED-CONTIG-LDST-SPEC--Advanced-SIMD-or-SVE-unaligned-contiguous-access>

##### `0x80B8`, ASE\_SVE\_UNALIGNED\_CONTIG\_LDST\_SPEC, Advanced SIMD or SVE unaligned contiguous access

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) Advanced SIMD or SVE contiguous load or store operation where the address is not aligned to the minimum of the in-memory size of the vector and the cache line size, in bytes.

The unaligned access is counted even if it is subsequently converted into multiple aligned accesses.

It is IMPLEMENTATION DEFINED which unaligned contiguous Advanced SIMD load or store operations are counted in AArch32 state.
