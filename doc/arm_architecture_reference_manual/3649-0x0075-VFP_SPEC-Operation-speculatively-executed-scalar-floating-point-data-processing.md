# ​0x0075, VFP_SPEC, Operation speculatively executed, scalar floating-point data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0075--VFP-SPEC--Operation-speculatively-executed--scalar-floating-point-data-processing>

##### `0x0075`, VFP\_SPEC, Operation speculatively executed, scalar floating-point data processing

The counter counts each operation counted by [INST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001B--INST-SPEC--Operation-speculatively-executed?lang=en#event_inst_spec) that is a scalar floating-point operation.

Operations due to the following instructions are counted as scalar floating-point data-processing operations:

- In AArch64 state:
  - The scalar floating-point operations from [Data processing - SIMD and floating-point](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point?lang=en#cegjeiei). Only the scalar operations are counted. SIMD floating-point operations are not counted.
  - Operations that take both an integer register and a floating-point register argument and perform a type conversion (to/from integer or to/from fixed-point): `FCVT{<mode>}`, `UCVTF`, and `SCVTF`.
- In AArch32 state:
  - Instructions from [Floating-point data-processing instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-14-Floating-point-data-processing-instructions?lang=en#babbgcfa).
  - Operations that take both an integer register and a floating-point register argument and perform a type conversion (to/from integer or to/from fixed-point): `VCVT<mode>` (floating-point), `VCVT`, `VCVTT`, and `VCVTB`.

This includes all scalar operations that operate on the SIMD&FP registers as floating-point values, except those that are counted as one of the following:

- SIMD scalar operations.
- Integer data-processing operations.
- Load or store operations.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
