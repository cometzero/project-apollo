# ​0x8004, SIMD_INST_SPEC, Operation speculatively executed, SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8004--SIMD-INST-SPEC--Operation-speculatively-executed--SIMD>

##### `0x8004`, SIMD\_INST\_SPEC, Operation speculatively executed, SIMD

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation due to any of:

- An Advanced SIMD data-processing operation. Advanced SIMD scalar data-processing operations are not counted.
- An SVE SIMD data-processing operation. SVE non-SIMD data-processing operations are not counted.
- An SME SIMD data-processing operation. SME non-SIMD data-processing operations are not counted.
- A structure load/store of one or more SIMD&FP registers.
- A load and replicate to one or more SIMD&FP registers.
- A scalar load/store of a SIMD&FP Q register or pair of Q registers.
- An SVE or SME load/store.

It is IMPLEMENTATION DEFINED which Advanced SIMD operations are counted in AArch32 state.

When Armv9.5 is not implemented, it is IMPLEMENTATION DEFINED whether scalar loads and stores to SIMD&FP registers other than those listed above are counted.

When Armv9.5 is implemented, other scalar loads and stores to SIMD&FP registers are not counted.
