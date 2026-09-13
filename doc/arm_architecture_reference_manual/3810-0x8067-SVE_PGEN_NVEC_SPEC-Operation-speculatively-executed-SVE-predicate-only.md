# ​0x8067, SVE_PGEN_NVEC_SPEC, Operation speculatively executed, SVE predicate-only

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8067--SVE-PGEN-NVEC-SPEC--Operation-speculatively-executed--SVE-predicate-only>

##### `0x8067`, SVE\_PGEN\_NVEC\_SPEC, Operation speculatively executed, SVE predicate-only

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicate-generating operation that does not read vector registers due to any of the following instructions:

- SVE: AND (predicates), ANDS, BIC (predicates), BICS, BRKA, BRKAS, BRKB, BRKBS, BRKN, BRKNS, BRKPA, BRKPAS, BRKPB, BRKPBS, EOR (predicates), EORS, NAND, NANDS, NOR, NORS, ORN (predicates), ORNS, ORR (predicates), ORRS, PFALSE, PFIRST, PNEXT, PTRUE (predicate), PTRUES, PUNPKHI, PUNPKLO, RDFFR, RDFFRS, REV (predicate), SEL (predicates), TRN1 (predicates), TRN2 (predicates), UZP1 (predicates), UZP2 (predicates), ZIP1 (predicates), or ZIP2 (predicates).
- SVE2: PEXT or PTRUE (predicate as counter).
