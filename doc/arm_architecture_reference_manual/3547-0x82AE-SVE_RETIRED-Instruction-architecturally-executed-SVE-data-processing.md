# ​0x82AE, SVE_RETIRED, Instruction architecturally executed, SVE data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82AE--SVE-RETIRED--Instruction-architecturally-executed--SVE-data-processing>

##### `0x82AE`, SVE\_RETIRED, Instruction architecturally executed, SVE data processing

The counter counts each [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) instruction counted by [ASE\_SVE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82A4--ASE-SVE-RETIRED--Instruction-architecturally-executed--Advanced-SIMD-data-processing-or-SVE-data-processing?lang=en#event_ase_sve_retired) that is classified as an SVE data-processing instruction.

An SVE data-processing instruction is any instruction that operates on the SVE scalable vector and predicate registers that is not any of the following:

- A load or store instruction. These are counted by [SVE\_INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8002--SVE-INST-RETIRED--Instruction-architecturally-executed--SVE?lang=en#event_sve_inst_retired).
- If the Cryptographic Extension is implemented, an instruction counted by [CRYPTO\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82AF--CRYPTO-RETIRED--Instruction-architecturally-executed--cryptographic-data-processing?lang=en#event_crypto_retired) as a Cryptographic data-processing instruction.
- When FEAT\_SME is implemented, an instruction counted by [SME\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835C--SME-SPEC--Operation-speculatively-executed--SME-data-processing?lang=en#event_sme_spec) as an SME data-processing instruction.
- A non-SIMD SVE instruction.

If the Cryptographic Extension and FEAT\_SVE2 are implemented, the SVE `PMULLB` and `PMULLT` (Q variants) instructions are not counted by [CRYPTO\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0077--CRYPTO-SPEC--Operation-speculatively-executed--cryptographic-data-processing?lang=en#event_crypto_spec) and are counted as SVE data-processing instructions.

Data-processing instructions defined by FEAT\_SME which involve the SVE registers but do not involve any ZA or ZT registers are counted as SVE data-processing instructions.
