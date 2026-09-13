# ​0x8040, INT_SPEC, Integer operation speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8040--INT-SPEC--Integer-operation-speculatively-executed>

##### `0x8040`, INT\_SPEC, Integer operation speculatively executed

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer arithmetic operation due to any of:

- An A64 scalar data-processing instruction.
- An Advanced SIMD instruction.
- An SVE data-processing instruction.
- An SME data-processing instruction.

It is IMPLEMENTATION DEFINED whether the counter counts any operation due to the following instructions:

- Scalar: `FABS`, `FNEG (scalar)`.
- Advanced SIMD: `FABS`, `FNEG (vector)`, `FRECPE`, `FRSQRTE`.
- SVE: `FABS`, `FEXPA`, `FNEG`, `FRECPE`, `FRSQRTE`, `FTSSEL`.
- Data movement instructions which move data without carrying out any operations on the data. This includes identity data-processing operations.
- Conditional select instructions.
- Floating-point conversion instructions.

Any operation counted by [FP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8010--FP-SPEC--Floating-point-operation-speculatively-executed--including-SIMD?lang=en#event_fp_spec) is not counted.

It is IMPLEMENTATION DEFINED which integer arithmetic operations are counted in AArch32 state.
