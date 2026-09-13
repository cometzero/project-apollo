# ​0x800B, ASE_SVE_UOP_SPEC, Microarchitectural operation speculatively executed, Advanced SIMD or SVE

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x800B--ASE-SVE-UOP-SPEC--Microarchitectural-operation-speculatively-executed--Advanced-SIMD-or-SVE>

##### `0x800B`, ASE\_SVE\_UOP\_SPEC, Microarchitectural operation speculatively executed, Advanced SIMD or SVE

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) microarchitectural operation counted by [UOP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8008--UOP-SPEC--Microarchitectural-operation-speculatively-executed?lang=en#event_uop_spec) due to an A64 Advanced SIMD or SVE instruction.

It is IMPLEMENTATION DEFINED whether the counter counts microarchitecural operations due to Advanced SIMD scalar and non-SIMD SVE instructions.

It is IMPLEMENTATION DEFINED which Advanced SIMD microarchitectural operations are counted in AArch32 state.
