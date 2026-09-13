# ​0x8062, SVE_PERM_XGRANULE_SPEC, Operation speculatively executed, SVE cross-granule permute

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8062--SVE-PERM-XGRANULE-SPEC--Operation-speculatively-executed--SVE-cross-granule-permute>

##### `0x8062`, SVE\_PERM\_XGRANULE\_SPEC, Operation speculatively executed, SVE cross-granule permute

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) vector or predicate permute operation that can cross between 128-bit vector granules or 16-bit predicate granules due to any of the following instructions:

- SVE: CLASTA, CLASTB, COMPACT, CPY (SIMD&FP scalar), CPY (scalar), DUP (indexed), DUP (scalar), EXT, INSR, LASTA, LASTB, PUNPKHI, PUNPKLO, REV (vector), SPLICE, SUNPKHI, SUNPKLO, TBL, TRN1 (predicates), TRN2 (predicates), UUNPKHI, UUNPKLO, UZP1, UZP2, ZIP1, or ZIP2.
- SVE2: EXPAND, TBX, or TBXQ.
