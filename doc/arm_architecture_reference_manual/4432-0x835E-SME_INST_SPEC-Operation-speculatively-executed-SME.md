# ​0x835E, SME_INST_SPEC, Operation speculatively executed, SME

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835E--SME-INST-SPEC--Operation-speculatively-executed--SME>

##### `0x835E`, SME\_INST\_SPEC, Operation speculatively executed, SME

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation counted by [SE\_INST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835F--SE-INST-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME?lang=en#event_se_inst_spec) that is classified as an SME operation.

An SME operation is any operation due to an instruction that operates on the ZA or ZT registers that is not any of the following:

- A non-SIMD SME operation.

Operations due to instructions defined by FEAT\_SME which involve the SVE registers but do not involve any ZA or ZT registers are counted as SVE operations.
