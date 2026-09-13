# ​0x8078, SVE_UNPRED_SPEC, Operation speculatively executed, SVE unpredicated

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8078--SVE-UNPRED-SPEC--Operation-speculatively-executed--SVE-unpredicated>

##### `0x8078`, SVE\_UNPRED\_SPEC, Operation speculatively executed, SVE unpredicated

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) SIMD operation due to any of:

- An SVE instruction without a Governing predicate operand.
- An SME instruction without any Governing predicate operand.

If FEAT\_SME is implemented, both operations due to SVE instructions and operations due to SME instructions with at least one Governing predicate operand that determines the Active elements are counted.
