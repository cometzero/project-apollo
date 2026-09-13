# ​0x8072, SVE_PLOOP_ELTS_SPEC, Operation speculatively executed, SVE predicate loop elements

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8072--SVE-PLOOP-ELTS-SPEC--Operation-speculatively-executed--SVE-predicate-loop-elements>

##### `0x8072`, SVE\_PLOOP\_ELTS\_SPEC, Operation speculatively executed, SVE predicate loop elements

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) loop predicate generation operation due to any of the following instructions:

- SVE: WHILELE (predicate), WHILELO (predicate), WHILELS (predicate), or WHILELT (predicate).
- SVE2: WHILEGE, WHILEGT, WHILEHI, WHILEHS, WHILELE, WHILELO, WHILELS, or WHILELT.

The counter increments by (128 ÷ CSIZE).

> #### Note
>
> Multiplying the counter value by (VL ÷ 128) determines the number of vector elements speculatively processed by while loops.
