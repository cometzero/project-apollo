# ​0x806D, SVE_PPERM_SPEC, Operation speculatively executed, SVE predicate permute

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x806D--SVE-PPERM-SPEC--Operation-speculatively-executed--SVE-predicate-permute>

##### `0x806D`, SVE\_PPERM\_SPEC, Operation speculatively executed, SVE predicate permute

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicate permute operation due to any of the following instructions:

- SVE: PUNPKHI, PUNPKLO, REV (predicate), TRN1 (predicates), TRN2 (predicates), UZP1 (predicates), UZP2 (predicates), ZIP1 (predicates), or ZIP2 (predicates).
