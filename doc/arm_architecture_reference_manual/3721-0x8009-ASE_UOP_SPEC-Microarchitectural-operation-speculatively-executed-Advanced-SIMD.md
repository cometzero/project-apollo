# ​0x8009, ASE_UOP_SPEC, Microarchitectural operation speculatively executed, Advanced SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8009--ASE-UOP-SPEC--Microarchitectural-operation-speculatively-executed--Advanced-SIMD>

##### `0x8009`, ASE\_UOP\_SPEC, Microarchitectural operation speculatively executed, Advanced SIMD

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) microarchitectural operation counted by [ASE\_SVE\_UOP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x800B--ASE-SVE-UOP-SPEC--Microarchitectural-operation-speculatively-executed--Advanced-SIMD-or-SVE?lang=en#event_ase_sve_uop_spec) due to an A64 Advanced SIMD instruction.

It is IMPLEMENTATION DEFINED whether the counter counts microarchitectural operations due to Advanced SIMD scalar instructions.

It is IMPLEMENTATION DEFINED which Advanced SIMD microarchitectural operations are counted in AArch32 state.
