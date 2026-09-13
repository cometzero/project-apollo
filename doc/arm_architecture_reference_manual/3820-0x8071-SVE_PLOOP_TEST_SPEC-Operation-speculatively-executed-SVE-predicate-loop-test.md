# ​0x8071, SVE_PLOOP_TEST_SPEC, Operation speculatively executed, SVE predicate loop test

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8071--SVE-PLOOP-TEST-SPEC--Operation-speculatively-executed--SVE-predicate-loop-test>

##### `0x8071`, SVE\_PLOOP\_TEST\_SPEC, Operation speculatively executed, SVE predicate loop test

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) loop predicate test operation due to any of the following instructions:

- SVE: BRKAS, BRKBS, BRKNS, BRKPAS, BRKPBS, WHILELE (predicate), WHILELO (predicate), WHILELS (predicate), or WHILELT (predicate).
- SVE2: WHILEGE, WHILEGT, WHILEHI, WHILEHS, WHILELE, WHILELO, WHILELS, or WHILELT.
