# ​0x8001, ASE_INST_RETIRED, Instruction architecturally executed, Advanced SIMD

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8001--ASE-INST-RETIRED--Instruction-architecturally-executed--Advanced-SIMD>

##### `0x8001`, ASE\_INST\_RETIRED, Instruction architecturally executed, Advanced SIMD

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) instruction counted by [ASE\_SVE\_INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8003--ASE-SVE-INST-RETIRED--Instruction-architecturally-executed--Advanced-SIMD-or-SVE?lang=en#event_ase_sve_inst_retired) that is classified as an Advanced SIMD instruction.

The following instructions are counted as Advanced SIMD instructions:

- For AArch64 state:
  - The SIMD operations listed in [Data processing - SIMD and floating-point](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point?lang=en#cegjeiei).
  - If [FEAT\_Crypto](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-1-The-Armv8-0-architecture-extension?lang=en#feat_feat_crypto) is implemented, the Advanced SIMD Cryptographic instructions. See [The Cryptographic Extension in AArch64 state](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point/-C3-8-30-The-Cryptographic-Extension-in-AArch64-state?lang=en#aa64_crypto_extension).
  - Advanced SIMD loads and stores.
- For AArch32 state:
  - Instructions from [Advanced SIMD data-processing instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-13-Advanced-SIMD-data-processing-instructions?lang=en#babcfidb).
  - If [FEAT\_Crypto](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-1-The-Armv8-0-architecture-extension?lang=en#feat_feat_crypto) is implemented, the `VMULL` (P64 variant) instruction. See [The Cryptographic Extension in AArch32 state](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-13-Advanced-SIMD-data-processing-instructions/-F2-13-11-The-Cryptographic-Extension-in-AArch32-state?lang=en#aa32_crypto_extension).

This includes all instructions that operate on the SIMD&FP registers, except those that are counted as one of the following:

- Integer data-processing instructions.
- Scalar floating-point data-processing instructions.

If FEAT\_PMUv3p9 is implemented, Advanced SIMD scalar instructions are not counted as Advanced SIMD instructions. Otherwise, it is IMPLEMENTATION DEFINED whether Advanced SIMD scalar instructions are counted as Advanced SIMD instructions. This includes Advanced SIMD scalar instructions which operate on floating-point values.
