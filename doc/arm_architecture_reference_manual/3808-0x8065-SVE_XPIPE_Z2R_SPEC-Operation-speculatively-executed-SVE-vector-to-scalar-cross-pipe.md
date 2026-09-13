# ​0x8065, SVE_XPIPE_Z2R_SPEC, Operation speculatively executed, SVE vector to scalar cross-pipe

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8065--SVE-XPIPE-Z2R-SPEC--Operation-speculatively-executed--SVE-vector-to-scalar-cross-pipe>

##### `0x8065`, SVE\_XPIPE\_Z2R\_SPEC, Operation speculatively executed, SVE vector to scalar cross-pipe

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) vector to general-purpose scalar cross-pipeline transfer operation counted by [SVE\_XPIPE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8064--SVE-XPIPE-SPEC--Operation-speculatively-executed--SVE-cross-pipe?lang=en#event_sve_xpipe_spec) due to any of the following instructions:

- SVE: CLASTA (scalar), CLASTB (scalar), CNTP (predicate), DECP (scalar), INCP (scalar), LASTA (scalar), LASTB (scalar), SQDECP (scalar), SQINCP (scalar), UQDECP (scalar), or UQINCP (scalar).
- SVE2: CNTP (predicate as counter), FIRSTP, or LASTP.
