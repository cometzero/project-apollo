# ​0x804A, SVE_INT_MUL_SPEC, Integer operation speculatively executed, SVE multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x804A--SVE-INT-MUL-SPEC--Integer-operation-speculatively-executed--SVE-multiply>

##### `0x804A`, SVE\_INT\_MUL\_SPEC, Integer operation speculatively executed, SVE multiply

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) integer multiply or multiply-accumulate operation counted by [ASE\_SVE\_INT\_MUL\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x804B--ASE-SVE-INT-MUL-SPEC--Integer-operation-speculatively-executed--Advanced-SIMD-or-SVE-multiply?lang=en#event_ase_sve_int_mul_spec) due to any of the following instructions:

- SVE: MAD, MLA (vectors), MLS (vectors), MSB, MUL, SMULH (predicated), or UMULH (predicated).
- SVE2: CMLA, MLA (indexed), MLS (indexed), MUL, PMUL, SMLALB, SMLALT, SMLSLB, SMLSLT, SMULH (unpredicated), SMULLB, SMULLT, SQDMLALB, SQDMLALBT, SQDMLALT, SQDMLSLB, SQDMLSLBT, SQDMLSLT, SQDMULH, SQDMULLB, SQDMULLT, SQRDCMLAH, SQRDMLAH, SQRDMLSH, SQRDMULH, UMLALB, UMLALT, UMLSLB, UMLSLT, UMULH (unpredicated), UMULLB, or UMULLT.
