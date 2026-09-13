# ​0x839B, SE_LUT_SPEC, Lookup table operation speculatively executed, Advanced SIMD, SVE, or SME data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x839B--SE-LUT-SPEC--Lookup-table-operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-data-processing>

##### `0x839B`, SE\_LUT\_SPEC, Lookup table operation speculatively executed, Advanced SIMD, SVE, or SME data processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) LUT operation counted by [SE\_INST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835F--SE-INST-SPEC--Operation-speculatively-executed--Advanced-SIMD--SVE--or-SME?lang=en#event_se_inst_spec) that returns a value from a lookup table made up of a ZT register, Z or V register which is indexed by values from a Z or V register.
