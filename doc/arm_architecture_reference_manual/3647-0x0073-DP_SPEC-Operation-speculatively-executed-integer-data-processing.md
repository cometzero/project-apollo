# ​0x0073, DP_SPEC, Operation speculatively executed, integer data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0073--DP-SPEC--Operation-speculatively-executed--integer-data-processing>

##### `0x0073`, DP\_SPEC, Operation speculatively executed, integer data processing

The counter counts each operation counted by [INST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001B--INST-SPEC--Operation-speculatively-executed?lang=en#event_inst_spec) that is an integer data-processing operation.

An integer data-processing operation is any operation that is not counted as any of the following:

- A load or store operation, counted by [LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0072--LDST-SPEC--Operation-speculatively-executed--load-or-store?lang=en#event_ldst_spec).
- A Software change of PC operation, counted by [PC\_WRITE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0076--PC-WRITE-SPEC--Operation-speculatively-executed--Software-change-of-the-PC?lang=en#event_pc_write_spec).
- A scalar floating-point data processing operation, counted by [VFP\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0075--VFP-SPEC--Operation-speculatively-executed--scalar-floating-point-data-processing?lang=en#event_vfp_spec).
- An Advanced SIMD, SVE or SME data processing operation, counted by [SE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835D--SE-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-data-processing?lang=en#event_se_spec).
- A cryptographic operation, counted by [CRYPTO\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0077--CRYPTO-SPEC--Operation-speculatively-executed--cryptographic-data-processing?lang=en#event_crypto_spec).

That is, operations due to the following instructions are counted as integer data-processing operations:

- In AArch64 state instructions from the following sections:
  - [Data processing - immediate](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-5-Data-processing---immediate?lang=en#chdfgjfj).
  - [Data processing - register](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-7-Data-processing---register?lang=en#chdicihg).
  - [System register instructions](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-1-Branches--Exception-generating--and-System-instructions/-C3-1-6-System-register-instructions?lang=en#chdcgcgh).
  - ‘Instructions with register argument’.
  - [System instructions](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-1-Branches--Exception-generating--and-System-instructions/-C3-1-7-System-instructions?lang=en#chdbagge) other than [Memory-writing instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions).
  - [Hint instructions](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C3-A64-Instruction-Set-Overview/-C3-1-Branches--Exception-generating--and-System-instructions/-C3-1-8-Hint-instructions?lang=en#chdbfbag).
  - When FEAT\_SVE is implemented and the [SVE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8056--SVE-SPEC--Operation-speculatively-executed--SVE-data-processing?lang=en#event_sve_spec) event is implemented, non-SIMD SVE instructions.
- In AArch32 state instructions from the following sections:
  - [Data-processing instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-4-Data-processing-instructions?lang=en#chddfdce).
  - [PSTATE and banked register access instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-5-PSTATE-and-banked-register-access-instructions?lang=en#chdcbhgc).
  - [Banked register access instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-5-PSTATE-and-banked-register-access-instructions/-F2-5-2-Banked-register-access-instructions?lang=en#cihceaaa).
  - [Miscellaneous instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-8-Miscellaneous-instructions?lang=en#babfcggg) other than `ISB` and prefetches.
  - [System register access instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-10-System-register-access-instructions?lang=en#chdbchcg) other than `LDC` and `STC` instructions.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
