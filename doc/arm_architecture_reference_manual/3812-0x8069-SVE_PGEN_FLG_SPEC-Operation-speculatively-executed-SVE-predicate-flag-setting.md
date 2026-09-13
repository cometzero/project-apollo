# ​0x8069, SVE_PGEN_FLG_SPEC, Operation speculatively executed, SVE predicate flag setting

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8069--SVE-PGEN-FLG-SPEC--Operation-speculatively-executed--SVE-predicate-flag-setting>

##### `0x8069`, SVE\_PGEN\_FLG\_SPEC, Operation speculatively executed, SVE predicate flag setting

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicate-generating operation that sets condition flags due to any of the following instructions:

- SVE: ANDS, BICS, BRKAS, BRKBS, BRKNS, BRKPAS, BRKPBS, CMP<cc>, EORS, NANDS, NORS, ORNS, ORRS, PFIRST, PNEXT, PTRUES, RDFFRS, WHILELE (predicate), WHILELO (predicate), WHILELS (predicate), or WHILELT (predicate).
- SVE2: MATCH, NMATCH, WHILEGE, WHILEGT, WHILEHI, WHILEHS, WHILELE, WHILELO, WHILELS, WHILELT, WHILERW, or WHILEWR.
