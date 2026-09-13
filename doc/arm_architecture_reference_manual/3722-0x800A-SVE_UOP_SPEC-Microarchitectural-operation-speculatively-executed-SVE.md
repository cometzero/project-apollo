# ​0x800A, SVE_UOP_SPEC, Microarchitectural operation speculatively executed, SVE

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x800A--SVE-UOP-SPEC--Microarchitectural-operation-speculatively-executed--SVE>

##### `0x800A`, SVE\_UOP\_SPEC, Microarchitectural operation speculatively executed, SVE

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) microarchitectural operation counted by [ASE\_SVE\_UOP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x800B--ASE-SVE-UOP-SPEC--Microarchitectural-operation-speculatively-executed--Advanced-SIMD-or-SVE?lang=en#event_ase_sve_uop_spec) due to an SVE instruction.

It is IMPLEMENTATION DEFINED whether the counter counts microarchitectural operations due to non-SIMD SVE instructions.
