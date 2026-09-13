# ​0x804D, SVE_INT_MUL64_SPEC, Integer operation speculatively executed, SVE 64×64 multiply

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x804D--SVE-INT-MUL64-SPEC--Integer-operation-speculatively-executed--SVE-64-64-multiply>

##### `0x804D`, SVE\_INT\_MUL64\_SPEC, Integer operation speculatively executed, SVE 64×64 multiply

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 64×64 integer multiply operation counted by [INT\_MUL64\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x804C--INT-MUL64-SPEC--Integer-operation-speculatively-executed--64-64-multiply?lang=en#event_int_mul64_spec) due to any of the following instructions:

- SVE: MAD, MLA (vectors), MLS (vectors), MSB, MUL (vectors, predicated), SMULH (predicated), or UMULH (predicated).
- SVE2: CMLA (vectors), MLA (indexed), MLS (indexed), MUL, SMULH (unpredicated), SQDMULH, SQRDCMLAH (vectors), SQRDMLAH, SQRDMLSH, SQRDMULH, or UMULH (unpredicated).

The counter only counts operations that perform a 64-bit × 64-bit integer multiply operations.
