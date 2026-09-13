# ​0x835C, SME_SPEC, Operation speculatively executed, SME data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835C--SME-SPEC--Operation-speculatively-executed--SME-data-processing>

##### `0x835C`, SME\_SPEC, Operation speculatively executed, SME data processing

The counter counts each operation counted by [SE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835D--SE-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-data-processing?lang=en#event_se_spec) that is an SME data-processing operation.

An SME data-processing operation is any operation due to an instruction that operates on the ZA or ZT registers that is not any of the following:

- A load or store operation. These are counted by [SME\_INST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835E--SME-INST-SPEC--Operation-speculatively-executed--SME?lang=en#event_sme_inst_spec).
- A non-SIMD SME operation.

Operations due to data-processing instructions defined by FEAT\_SME which involve the SVE registers but do not involve any ZA or ZT registers are counted as SVE data-processing operations.
