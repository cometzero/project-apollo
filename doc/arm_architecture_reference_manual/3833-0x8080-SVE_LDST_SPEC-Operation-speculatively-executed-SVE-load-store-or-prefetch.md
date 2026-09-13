# ​0x8080, SVE_LDST_SPEC, Operation speculatively executed, SVE load, store, or prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8080--SVE-LDST-SPEC--Operation-speculatively-executed--SVE-load--store--or-prefetch>

##### `0x8080`, SVE\_LDST\_SPEC, Operation speculatively executed, SVE load, store, or prefetch

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from or writes to memory counted by [ASE\_SVE\_LDST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8084--ASE-SVE-LDST-SPEC--Operation-speculatively-executed--Advanced-SIMD-or-SVE-load-or-store?lang=en#event_ase_sve_ldst_spec) due to an SVE load, store, or prefetch instruction.

The following are classified as SVE load, store and prefetch instructions:

- Any load which reads from an SVE register.
- Any store which writes to an SVE register.
- Any of the following prefetch instructions which accept a Governing predicate:
  - `PRFB`.
  - `PRFD`.
  - `PRFH`.
  - `PRFW`.

When FEAT\_SME is implemented, this includes SME loads and stores of the SVE Z vectors. SME loads and stores of the ZA and ZT registers are not counted.
