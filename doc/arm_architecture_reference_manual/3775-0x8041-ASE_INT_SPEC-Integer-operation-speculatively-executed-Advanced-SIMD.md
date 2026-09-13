# ​0x8041, ASE_INT_SPEC, Integer operation speculatively executed, Advanced SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8041--ASE-INT-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD>

##### `0x8041`, ASE\_INT\_SPEC, Integer operation speculatively executed, Advanced SIMD

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer operation counted by [ASE\_SVE\_INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8043--ASE-SVE-INT-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE?lang=en#event_ase_sve_int_spec) due to an A64 Advanced SIMD instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD integer operations are counted in AArch32 state.
