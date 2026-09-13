# ​0x8048, INT_MUL_SPEC, Integer operation speculatively executed, multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8048--INT-MUL-SPEC--Integer-operation-speculatively-executed--multiply>

##### `0x8048`, INT\_MUL\_SPEC, Integer operation speculatively executed, multiply

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer multiply or multiply-accumulate operation counted by [INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8040--INT-SPEC--Integer-operation-speculatively-executed?lang=en#event_int_spec) due to any of the following A64 instructions:

- Scalar: MADD, MSUB, MUL, SMADDL, SMULH, UMADDL, or UMULH.
- Advanced SIMD: MLA, MLS, MUL, PMUL, PMULL, PMULL2, SMLAL, SMLAL2, SMLSL, SMLSL2, SMULL, SMULL2, SQDMLAL, SQDMLAL2, SQDMLSL, SQDMLSL2, SQDMULH, SQDMULL, SQDMULL2, SQRDMULH, UMLAL, UMLAL2, UMLSL, UMLSL2, UMULL, or UMULL2.
- When FEAT\_RDM is implemented, Advanced SIMD: SQRDMLAH or SQRDMLSH.
- SVE: MAD, MLA (vectors), MLS (vectors), MSB, MUL, SMULH (predicated), or UMULH (predicated).
- SVE2: CMLA, MLA (indexed), MLS (indexed), MUL, PMUL, SMLALB, SMLALT, SMLSLB, SMLSLT, SMULH (unpredicated), SMULLB, SMULLT, SQDMLALB, SQDMLALBT, SQDMLALT, SQDMLSLB, SQDMLSLBT, SQDMLSLT, SQDMULH, SQDMULLB, SQDMULLT, SQRDCMLAH, SQRDMLAH, SQRDMLSH, SQRDMULH, UMLALB, UMLALT, UMLSLB, UMLSLT, UMULH (unpredicated), UMULLB, or UMULLT.
- SME2: SMLAL, SMLALL, SMLSL, SMLSLL, SUMLALL, UMLAL, UMLALL, UMLSL, UMLSLL, or USMLALL.

It is IMPLEMENTATION DEFINED which integer multiply or multiply-accumulate operations are counted in AArch32 state.
