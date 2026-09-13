# ​0x82AB, DP_RETIRED, Instruction architecturally executed, integer data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82AB--DP-RETIRED--Instruction-architecturally-executed--integer-data-processing>

##### `0x82AB`, DP\_RETIRED, Instruction architecturally executed, integer data processing

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) instruction counted by [INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed?lang=en#event_inst_retired) that is classified as an integer data-processing instruction.

An integer data-processing instruction is any instruction that is not counted as any of the following:

- A load or store instruction, counted by [LD\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0006--LD-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--load?lang=en#event_ld_retired) or [ST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0007--ST-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--store?lang=en#event_st_retired).
- A Software change of PC instruction, counted by [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired).
- A scalar floating-point data processing instruction, counted by [VFP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82AD--VFP-RETIRED--Instruction-architecturally-executed--scalar-floating-point-data-processing?lang=en#event_vfp_retired).
- An Advanced SIMD, SVE or SME data processing instruction, counted by [SE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8359--SE-RETIRED--Instruction-architecturally-executed--Advanced-SIMD--SVE--or-SME-data-processing?lang=en#event_se_retired).
- A cryptographic instruction, counted by [CRYPTO\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82AF--CRYPTO-RETIRED--Instruction-architecturally-executed--cryptographic-data-processing?lang=en#event_crypto_retired).

That is, the following instructions are counted as integer data-processing instructions:

- In AArch64 state:
  - Instructions from [Data processing - immediate](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-5-Data-processing---immediate?lang=en#chdfgjfj).
  - Instructions from [Data processing - register](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-7-Data-processing---register?lang=en#chdicihg).
  - Instructions from [System register instructions](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-1-Branches--Exception-generating--and-System-instructions/-C3-1-6-System-register-instructions?lang=en#chdcgcgh).
  - Instructions from ‘Instructions with register argument’.
  - Instructions from [System instructions](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-1-Branches--Exception-generating--and-System-instructions/-C3-1-7-System-instructions?lang=en#chdbagge) other than [Memory-writing instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions).
  - Instructions from [Hint instructions](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-1-Branches--Exception-generating--and-System-instructions/-C3-1-8-Hint-instructions?lang=en#chdbfbag).
  - Instructions from [Floating-point move (register)](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point/-C3-8-2-Floating-point-move--register-?lang=en#chddffab) that transfer data between a general-purpose register and a SIMD&FP register without conversion: `FMOV` (general).
  - Instructions from [SIMD move](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-8-Data-processing---SIMD-and-floating-point/-C3-8-12-SIMD-move?lang=en#chddbejc) that transfer data between a general-purpose register and an element or elements in a SIMD&FP register: `DUP` (general), `SMOV`, `UMOV`, and `INS` (general). This includes the aliases `MOV` (from general) and `MOV` (to general).
  - When FEAT\_SVE is implemented, non-SIMD SVE instructions.
- In AArch32 state:
  - Instructions from [Data-processing instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-4-Data-processing-instructions?lang=en#chddfdce).
  - Instructions from [PSTATE and banked register access instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-5-PSTATE-and-banked-register-access-instructions?lang=en#chdcbhgc).
  - Instructions from [Banked register access instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-5-PSTATE-and-banked-register-access-instructions/-F2-5-2-Banked-register-access-instructions?lang=en#cihceaaa).
  - Instructions from [Miscellaneous instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-8-Miscellaneous-instructions?lang=en#babfcggg) other than `ISB` and prefetches.
  - Instructions from [System register access instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-10-System-register-access-instructions?lang=en#chdbchcg) other than `LDC` and `STC` instructions.
  - `VDUP` (general-purpose register).
  - All `VMOV` instructions that transfer data between a general-purpose register and a SIMD&FP register.
  - `VMRS` and `VMSR`.
