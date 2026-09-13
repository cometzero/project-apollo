# ​0x8002, SVE_INST_RETIRED, Instruction architecturally executed, SVE

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8002--SVE-INST-RETIRED--Instruction-architecturally-executed--SVE>

##### `0x8002`, SVE\_INST\_RETIRED, Instruction architecturally executed, SVE

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) instruction counted by [ASE\_SVE\_INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8003--ASE-SVE-INST-RETIRED--Instruction-architecturally-executed--Advanced-SIMD-or-SVE?lang=en#event_ase_sve_inst_retired) that is classified as an SVE instruction.

An SVE instruction is any instruction that operates on the SVE scalable vector and predicate registers that is not any of the following:

- When FEAT\_SME is implemented, an instruction counted by [SME\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835C--SME-SPEC--Operation-speculatively-executed--SME-data-processing?lang=en#event_sme_spec) as an SME instruction.
- If FEAT\_PMUv3p9 is implemented, a non-SIMD SVE instruction.

If FEAT\_PMUv3p9 is not implemented, it is IMPLEMENTATION DEFINED whether the counter counts non-SIMD instructions.

Instructions defined by FEAT\_SME which involve the SVE registers but do not involve any ZA or ZT registers are counted as SVE instructions.
