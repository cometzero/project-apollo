# ​0x8358, SME_RETIRED, Instruction architecturally executed, SME data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8358--SME-RETIRED--Instruction-architecturally-executed--SME-data-processing>

##### `0x8358`, SME\_RETIRED, Instruction architecturally executed, SME data processing

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) instruction counted by [SE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8359--SE-RETIRED--Instruction-architecturally-executed--Advanced-SIMD--SVE--or-SME-data-processing?lang=en#event_se_retired) that is classified as an SME data-processing instruction.

An SME data-processing instruction is any instruction that operates on the ZA or ZT registers that is not any of the following:

- A load or store instruction. These are counted by [SME\_INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835A--SME-INST-RETIRED--Instruction-architecturally-executed--SME?lang=en#event_sme_inst_retired).
- A non-SIMD SME instruction.

Data-processing instructions defined by FEAT\_SME which involve the SVE registers but do not involve any ZA or ZT registers are counted as SVE data-processing instructions.
