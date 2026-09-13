# ​0x806F, SVE_PCNT_SPEC, Operation speculatively executed, SVE predicate count

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x806F--SVE-PCNT-SPEC--Operation-speculatively-executed--SVE-predicate-count>

##### `0x806F`, SVE\_PCNT\_SPEC, Operation speculatively executed, SVE predicate count

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) predicate population count operation due to any of the following instructions:

- SVE: CNTP (predicate), DECP, INCP, SQDECP, SQINCP, UQDECP, or UQINCP.
- SVE2: CNTP (predicate as counter).
