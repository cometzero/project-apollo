# ​0x800C, SIMD_UOP_SPEC, Microarchitectural operation speculatively executed, SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x800C--SIMD-UOP-SPEC--Microarchitectural-operation-speculatively-executed--SIMD>

##### `0x800C`, SIMD\_UOP\_SPEC, Microarchitectural operation speculatively executed, SIMD

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) microarchitectural operation counted by [UOP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8008--UOP-SPEC--Microarchitectural-operation-speculatively-executed?lang=en#event_uop_spec) due to any of:

- An SVE instruction other than non-SIMD SVE instructions.
- An A64 Advanced SIMD instruction other than an Advanced SIMD scalar instruction.

It is IMPLEMENTATION DEFINED which Advanced SIMD microarchitectural operations are counted in AArch32 state.
