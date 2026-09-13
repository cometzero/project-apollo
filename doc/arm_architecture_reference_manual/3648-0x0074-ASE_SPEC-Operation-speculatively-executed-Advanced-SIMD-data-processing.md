# ​0x0074, ASE_SPEC, Operation speculatively executed, Advanced SIMD data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0074--ASE-SPEC--Operation-speculatively-executed--Advanced-SIMD-data-processing>

##### `0x0074`, ASE\_SPEC, Operation speculatively executed, Advanced SIMD data processing

The counter counts each operation counted by [ASE\_SVE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8057--ASE-SVE-SPEC--Operation-speculatively-executed--Advanced-SIMD-data-processing-or-SVE-data-processing?lang=en#event_ase_sve_spec) that is an Advanced SIMD data-processing operation.

Operations due to the following instructions are counted as Advanced SIMD data-processing operations:

- For AArch64 state:
  - The SIMD operations listed in [Data processing - SIMD and floating-point](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point?lang=en#cegjeiei).
  - Advanced SIMD scalar instructions, including those which operate on floating-point values.
  - If [FEAT\_Crypto](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-1-The-Armv8-0-architecture-extension?lang=en#feat_feat_crypto) is implemented, the Advanced SIMD `PMULL` and `PMULL2` (1Q variants) instructions. See [The Cryptographic Extension in AArch64 state](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point/-C3-8-30-The-Cryptographic-Extension-in-AArch64-state?lang=en#aa64_crypto_extension).
- For AArch32 state:
  - Instructions from [Advanced SIMD data-processing instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-13-Advanced-SIMD-data-processing-instructions?lang=en#babcfidb).
  - If [FEAT\_Crypto](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-1-The-Armv8-0-architecture-extension?lang=en#feat_feat_crypto) is implemented, the `VMULL` (P64 variant) instruction. See [The Cryptographic Extension in AArch32 state](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-13-Advanced-SIMD-data-processing-instructions/-F2-13-11-The-Cryptographic-Extension-in-AArch32-state?lang=en#aa32_crypto_extension).

This includes all operations that operate on the SIMD&FP registers, except those that are counted as one of the following:

- Integer data-processing operations.
- Scalar floating-point data-processing operations.
- Load or store operations.
- Cryptographic data-processing operations counted by [CRYPTO\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0077--CRYPTO-SPEC--Operation-speculatively-executed--cryptographic-data-processing?lang=en#event_crypto_spec). [CRYPTO\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0077--CRYPTO-SPEC--Operation-speculatively-executed--cryptographic-data-processing?lang=en#event_crypto_spec) does not count the Cryptographic data-processing operations included above.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
