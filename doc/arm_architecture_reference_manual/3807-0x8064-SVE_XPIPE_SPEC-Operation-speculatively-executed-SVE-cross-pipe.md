# ​0x8064, SVE_XPIPE_SPEC, Operation speculatively executed, SVE cross-pipe

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8064--SVE-XPIPE-SPEC--Operation-speculatively-executed--SVE-cross-pipe>

##### `0x8064`, SVE\_XPIPE\_SPEC, Operation speculatively executed, SVE cross-pipe

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) cross-pipeline transfer operation due to any of the following instructions:

- SVE: CLASTA (scalar), CLASTB (scalar), CNTP (predicate), CPY (scalar), DECP (scalar), DUP (scalar), INCP (scalar), INDEX (immediate, scalar), INDEX (scalar, immediate), INDEX (scalars), INSR (scalar), LASTA (scalar), LASTB (scalar), SQDECP (scalar), SQINCP (scalar), UQDECP (scalar), UQINCP (scalar), WHILELE (predicate), WHILELO (predicate), WHILELS (predicate), or WHILELT (predicate).
- SVE2: CNTP (predicate as counter), FIRSTP, LASTP, PSEL, WHILEGE, WHILEGT, WHILEHI, WHILEHS, WHILELE, WHILELO, WHILELS, WHILELT, WHILERW, or WHILEWR.
