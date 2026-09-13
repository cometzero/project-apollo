# ​0x8068, SVE_PGEN_SPEC, Operation speculatively executed, SVE predicate generating

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8068--SVE-PGEN-SPEC--Operation-speculatively-executed--SVE-predicate-generating>

##### `0x8068`, SVE\_PGEN\_SPEC, Operation speculatively executed, SVE predicate generating

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicate-generating operation due to any of the following instructions:

- SVE: AND (predicates), ANDS, BIC (predicates), BICS, BRKA, BRKAS, BRKB, BRKBS, BRKN, BRKNS, BRKPA, BRKPAS, BRKPB, BRKPBS, CMP<cc>, EOR (predicates), EORS, FAC<cc>, FCM<cc>, NAND, NANDS, NOR, NORS, ORN (predicates), ORNS, ORR (predicates), ORRS, PFALSE, PFIRST, PNEXT, PTRUE (predicate), PTRUES, PUNPKHI, PUNPKLO, RDFFR, RDFFRS, REV (predicate), SEL (predicates), TRN1 (predicates), TRN2 (predicates), UZP1 (predicates), UZP2 (predicates), WHILELE (predicate), WHILELO (predicate), WHILELS (predicate), WHILELT (predicate), ZIP1 (predicates), or ZIP2 (predicates).
- SVE2: MATCH, NMATCH, PEXT, PMOV (to predicate), PSEL, PTRUE (predicate as counter), WHILEGE, WHILEGT, WHILEHI, WHILEHS, WHILELE, WHILELO, WHILELS, WHILELT, WHILERW, or WHILEWR.
