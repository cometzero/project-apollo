# ​0x8066, SVE_XPIPE_R2Z_SPEC, Operation speculatively executed, SVE scalar to vector cross-pipe

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8066--SVE-XPIPE-R2Z-SPEC--Operation-speculatively-executed--SVE-scalar-to-vector-cross-pipe>

##### `0x8066`, SVE\_XPIPE\_R2Z\_SPEC, Operation speculatively executed, SVE scalar to vector cross-pipe

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) general-purpose scalar to vector cross-pipeline transfer operation counted by [SVE\_XPIPE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8064--SVE-XPIPE-SPEC--Operation-speculatively-executed--SVE-cross-pipe?lang=en#event_sve_xpipe_spec) due to any of the following instructions:

- SVE: CPY (scalar), DUP (scalar), INDEX (immediate, scalar), INDEX (scalar, immediate), INDEX (scalars), INSR (scalar), WHILELE (predicate), WHILELO (predicate), WHILELS (predicate), or WHILELT (predicate).
- SVE2: PSEL, WHILEGE, WHILEGT, WHILEHI, WHILEHS, WHILELE, WHILELO, WHILELS, WHILELT, WHILERW, or WHILEWR.
