# ​0x8084, ASE_SVE_LDST_SPEC, Operation speculatively executed, Advanced SIMD or SVE load or store

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8084--ASE-SVE-LDST-SPEC--Operation-speculatively-executed--Advanced-SIMD-or-SVE-load-or-store>

##### `0x8084`, ASE\_SVE\_LDST\_SPEC, Operation speculatively executed, Advanced SIMD or SVE load or store

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from or writes to memory due to an A64 Advanced SIMD or SVE load, store, or prefetch instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD load or store operations are counted in AArch32 state.
