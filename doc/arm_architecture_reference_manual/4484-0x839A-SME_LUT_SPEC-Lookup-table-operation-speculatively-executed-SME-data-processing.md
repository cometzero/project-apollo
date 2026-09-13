# ​0x839A, SME_LUT_SPEC, Lookup table operation speculatively executed, SME data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x839A--SME-LUT-SPEC--Lookup-table-operation-speculatively-executed--SME-data-processing>

##### `0x839A`, SME\_LUT\_SPEC, Lookup table operation speculatively executed, SME data processing

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) LUT operation counted by [SE\_LUT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x839B--SE-LUT-SPEC--Lookup-table-operation-speculatively-executed--Advanced-SIMD--SVE--or-SME-data-processing?lang=en#event_se_lut_spec) that returns a value from a lookup table made up of a ZT register which is indexed by values from a Z register.

That is, due to any of the following instructions:

- SME2: LUTI2 or LUTI4.
