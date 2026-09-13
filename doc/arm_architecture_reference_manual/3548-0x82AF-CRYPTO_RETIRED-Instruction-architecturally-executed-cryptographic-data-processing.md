# ​0x82AF, CRYPTO_RETIRED, Instruction architecturally executed, cryptographic data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82AF--CRYPTO-RETIRED--Instruction-architecturally-executed--cryptographic-data-processing>

##### `0x82AF`, CRYPTO\_RETIRED, Instruction architecturally executed, cryptographic data processing

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) instruction counted by [INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed?lang=en#event_inst_retired) that is classified as a cryptographic instruction.

The following instructions are counted as cryptographic data-processing instructions:

- In AArch64 state, instructions from the following sections:
  - [The Cryptographic Extension in AArch64 state](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point/-C3-8-30-The-Cryptographic-Extension-in-AArch64-state?lang=en#aa64_crypto_extension) other than the Advanced SIMD `PMULL` and `PMULL2` (1Q variants) instructions.
  - If FEAT\_SVE2 is implemented, SVE2 Crypto Extensions other than the SVE `PMULLB` and `PMULLT` (Q variants) instructions.
- In AArch32 state, instructions from [The Cryptographic Extension in AArch32 state](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-13-Advanced-SIMD-data-processing-instructions/-F2-13-11-The-Cryptographic-Extension-in-AArch32-state?lang=en#aa32_crypto_extension) other than `VMULL` (P64 variant).
