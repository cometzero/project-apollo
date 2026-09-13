# ​0x8073, SVE_PLOOP_TERM_SPEC, Operation speculatively executed, SVE predicate loop termination

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8073--SVE-PLOOP-TERM-SPEC--Operation-speculatively-executed--SVE-predicate-loop-termination>

##### `0x8073`, SVE\_PLOOP\_TERM\_SPEC, Operation speculatively executed, SVE predicate loop termination

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) loop-terminating predicate generation operation due to any of:

- An SVE `WHILELE`, `WHILELO`, `WHILELS`, or `WHILELT` instruction which sets [PSTATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-5-Process-state--PSTATE?lang=en#pstate).N to 0.
- An SVE `BRKAS`, `BRKBS`, `BRKNS`, `BRKPAS`, or `BRKPBS` instruction which sets [PSTATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-5-Process-state--PSTATE?lang=en#pstate).C to 1.
- An SVE `CTERMEQ` or `CTERMNE` instruction which sets [PSTATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-5-Process-state--PSTATE?lang=en#pstate).N to 1 and [PSTATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-5-Process-state--PSTATE?lang=en#pstate).V to 0.
- An SVE2 `WHILEGE`, `WHILEGT`, `WHILEHI`, or `WHILEHS` instruction which sets [PSTATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-5-Process-state--PSTATE?lang=en#pstate).N to 0.
