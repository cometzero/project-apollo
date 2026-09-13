# ​0x804F, SVE_INT_MULH64_SPEC, Integer operation speculatively executed, SVE 64×64 multiply high part

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x804F--SVE-INT-MULH64-SPEC--Integer-operation-speculatively-executed--SVE-64-64-multiply-high-part>

##### `0x804F`, SVE\_INT\_MULH64\_SPEC, Integer operation speculatively executed, SVE 64×64 multiply high part

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) 64×64 integer multiply returning high part operation counted by [INT\_MULH64\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x804E--INT-MULH64-SPEC--Integer-operation-speculatively-executed--64-64-multiply-returning-high-part?lang=en#event_int_mulh64_spec) due to any of the following instructions:

- SVE: SMULH (predicated) or UMULH (predicated).
- SVE2: SMULH (unpredicated), SQDMULH, SQRDMULH, or UMULH (unpredicated).
