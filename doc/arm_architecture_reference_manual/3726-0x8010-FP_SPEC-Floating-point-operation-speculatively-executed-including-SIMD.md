# ​0x8010, FP_SPEC, Floating-point operation speculatively executed, including SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD>

##### `0x8010`, FP\_SPEC, Floating-point operation speculatively executed, including SIMD

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point data-processing operation due to any of:

- An A64 scalar instruction.
- An A64 Advanced SIMD instruction.
- An SVE instruction.
- An SME instruction.

From Armv9.5, if FEAT\_AFP is implemented, then the counter counts any operation due to any of the following instructions:

- Scalar: `FABS`, or `FNEG (scalar)`.
- Advanced SIMD: `FABS`, `FNEG (vector)`, `FRECPE`, or `FRSQRTE`.
- SVE: `FABS`, `FEXPA`, `FNEG`, `FRECPE`, `FRSQRTE`, or `FTSSEL`.

Otherwise, it is IMPLEMENTATION DEFINED whether the counter counts any operation due to the above instructions.

It is IMPLEMENTATION DEFINED whether the counter counts any operations due to the following instructions:

- Data movement instructions which move data without carrying out any operations on the data. This includes identity data-processing operations.
- Conditional select instructions.
- Floating-point conversion instructions.

Any operation counted by [INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8040--INT-SPEC--Integer-operation-speculatively-executed?lang=en#event_int_spec) is not counted.

It is IMPLEMENTATION DEFINED which floating-point data-processing operations are counted in AArch32 state.

Arm recommends that if [FP\_CVT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8038--FP-CVT-SPEC--Floating-point-operation-speculatively-executed--convert?lang=en#event_fp_cvt_spec) is implemented, [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec) counts operations due to convert instructions.

> #### Note
>
> This event differs from the [VFP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0075--VFP-SPEC--Operation-speculatively-executed--scalar-floating-point-data-processing?lang=en#event_vfp_spec) event which does not count SIMD operations.
