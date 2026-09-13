# ​0x8038, FP_CVT_SPEC, Floating-point operation speculatively executed, convert

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8038--FP-CVT-SPEC--Floating-point-operation-speculatively-executed--convert>

##### `0x8038`, FP\_CVT\_SPEC, Floating-point operation speculatively executed, convert

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) floating-point convert operation due to any of:

- An A64 scalar floating-point conversion instruction.
- An Advanced SIMD floating-point conversion instruction.
- An SVE register targeting floating-point conversion instruction.

This includes both conversions between floating-point types, and conversions between integer and floating-point types.

It is IMPLEMENTATION DEFINED which floating-point convert operations are counted in AArch32 state.
