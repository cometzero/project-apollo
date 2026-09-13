# ​0x8060, SVE_PERM_SPEC, Operation speculatively executed, SVE permute

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8060--SVE-PERM-SPEC--Operation-speculatively-executed--SVE-permute>

##### `0x8060`, SVE\_PERM\_SPEC, Operation speculatively executed, SVE permute

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) vector or predicate permute operation due to any of the following instructions:

- SVE: CLASTA, CLASTB, COMPACT, CPY (SIMD&FP scalar), CPY (scalar), DUP (indexed), DUP (scalar), EXT, INSR, LASTA, LASTB, PUNPKHI, PUNPKLO, REV (vector), REVB, REVH, REVW, SPLICE, SUNPKHI, SUNPKLO, TBL, TRN1, TRN2, UUNPKHI, UUNPKLO, UZP1, UZP2, ZIP1, or ZIP2.
- SVE2: EXPAND, REVD, TBX, or TBXQ.
