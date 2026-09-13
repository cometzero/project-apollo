# ​0x8070, SVE_PLOOP_WHILE_SPEC, Operation speculatively executed, SVE predicate loop while

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8070--SVE-PLOOP-WHILE-SPEC--Operation-speculatively-executed--SVE-predicate-loop-while>

##### `0x8070`, SVE\_PLOOP\_WHILE\_SPEC, Operation speculatively executed, SVE predicate loop while

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) counted predicate generation operation due to any of the following instructions:

- SVE: WHILELE (predicate), WHILELO (predicate), WHILELS (predicate), or WHILELT (predicate).
- SVE2: WHILEGE, WHILEGT, WHILEHI, WHILEHS, WHILELE, WHILELO, WHILELS, or WHILELT.
