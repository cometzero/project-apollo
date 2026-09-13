# ​0x804E, INT_MULH64_SPEC, Integer operation speculatively executed, 64×64 multiply returning high part

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x804E--INT-MULH64-SPEC--Integer-operation-speculatively-executed--64-64-multiply-returning-high-part>

##### `0x804E`, INT\_MULH64\_SPEC, Integer operation speculatively executed, 64×64 multiply returning high part

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) widening 64×64 integer multiply operation counted by [INT\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8040--INT-SPEC--Integer-operation-speculatively-executed?lang=en#event_int_spec) due to any of the following A64 instructions:

- Scalar: SMULH or UMULH.
- SVE: SMULH (predicated) or UMULH (predicated).
- SVE2: SMULH (unpredicated), SQDMULH, SQRDMULH, or UMULH (unpredicated).

These instructions perform 64-bit × 64-bit integer multiply operations.
