# ​0x82AD, VFP_RETIRED, Instruction architecturally executed, scalar floating-point data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82AD--VFP-RETIRED--Instruction-architecturally-executed--scalar-floating-point-data-processing>

##### `0x82AD`, VFP\_RETIRED, Instruction architecturally executed, scalar floating-point data processing

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) instruction counted by [INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed?lang=en#event_inst_retired) that is classified as a scalar floating-point instruction.

The following instructions are counted as scalar floating-point data-processing instructions:

- In AArch64 state:
  - The scalar floating-point instructions from [Data processing - SIMD and floating-point](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point?lang=en#cegjeiei). Only the scalar instructions are counted. SIMD floating-point instructions are not counted.
  - Instructions that take both an integer register and a floating-point register argument and perform a type conversion (to/from integer or to/from fixed-point): `FCVT{<mode>}`, `UCVTF`, and `SCVTF`.
- In AArch32 state:
  - Instructions from [Floating-point data-processing instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-14-Floating-point-data-processing-instructions?lang=en#babbgcfa).
  - Instructions that take both an integer register and a floating-point register argument and perform a type conversion (to/from integer or to/from fixed-point): `VCVT<mode>` (floating-point), `VCVT`, `VCVTT`, and `VCVTB`.

This includes all scalar instructions that operate on the SIMD&FP registers as floating-point values, except those that are counted as one of the following:

- SIMD scalar instructions.
- Integer data-processing instructions.
- Load or store instructions.
