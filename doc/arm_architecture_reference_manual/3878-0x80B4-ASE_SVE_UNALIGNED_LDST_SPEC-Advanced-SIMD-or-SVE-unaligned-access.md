# ​0x80B4, ASE_SVE_UNALIGNED_LDST_SPEC, Advanced SIMD or SVE unaligned access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B4--ASE-SVE-UNALIGNED-LDST-SPEC--Advanced-SIMD-or-SVE-unaligned-access>

##### `0x80B4`, ASE\_SVE\_UNALIGNED\_LDST\_SPEC, Advanced SIMD or SVE unaligned access

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) A64 Advanced SIMD or SVE load or store instruction where either:

- A contiguous vector address is not aligned to the minimum of the in-memory size of the vector and the cache line size, in bytes.
- A gather, scatter, or single element address is not aligned to the memory element access size, in bytes.

The unaligned access is counted even if it is subsequently converted into multiple aligned accesses.

It is IMPLEMENTATION DEFINED which unaligned Advanced SIMD load or store operations are counted in AArch32 state.
