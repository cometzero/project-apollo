# ​0x8000, SIMD_INST_RETIRED, Instruction architecturally executed, SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8000--SIMD-INST-RETIRED--Instruction-architecturally-executed--SIMD>

##### `0x8000`, SIMD\_INST\_RETIRED, Instruction architecturally executed, SIMD

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) SIMD instruction counted by [INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed?lang=en#event_inst_retired) due to any of:

- An Advanced SIMD data-processing instruction. Advanced SIMD scalar data-processing instructions are not counted.
- An SVE SIMD data-processing instruction. SVE non-SIMD data-processing instructions are not counted.
- An SME SIMD data-processing instruction. SME non-SIMD data-processing instructions are not counted.
- A structure load/store of one or more SIMD&FP registers.
- A load and replicate to one or more SIMD&FP registers.
- A scalar load/store of a SIMD&FP Q register or pair of Q registers.
- An SVE or SME load/store.

It is IMPLEMENTATION DEFINED which [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) SIMD instructions are counted in AArch32 state.

When Armv9.5 is not implemented, it is IMPLEMENTATION DEFINED whether scalar loads and stores to SIMD&FP registers other than those listed above are counted.

When Armv9.5 is implemented, other scalar loads and stores to SIMD&FP registers are not counted.
