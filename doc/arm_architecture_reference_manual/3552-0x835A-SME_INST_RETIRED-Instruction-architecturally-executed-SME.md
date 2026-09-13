# ​0x835A, SME_INST_RETIRED, Instruction architecturally executed, SME

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835A--SME-INST-RETIRED--Instruction-architecturally-executed--SME>

##### `0x835A`, SME\_INST\_RETIRED, Instruction architecturally executed, SME

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) instruction counted by [SE\_INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835B--SE-INST-RETIRED--Instruction-architecturally-executed--Advanced-SIMD--SVE--or-SME?lang=en#event_se_inst_retired) that is classified as an SME instruction.

An SME instruction is any instruction that operates on the ZA or ZT registers that is not any of the following:

- A non-SIMD SME instruction.

Instructions defined by FEAT\_SME which involve the SVE registers but do not involve any ZA or ZT registers are counted as SVE instructions.
