# ​0x80B1, SVE_LD64_GATHER_SPEC, Operation speculatively executed, SVE 64-bit gather-load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B1--SVE-LD64-GATHER-SPEC--Operation-speculatively-executed--SVE-64-bit-gather-load>

##### `0x80B1`, SVE\_LD64\_GATHER\_SPEC, Operation speculatively executed, SVE 64-bit gather-load

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) operation that reads from memory counted by [SVE\_LDST64\_NONCONTIG\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80B0--SVE-LDST64-NONCONTIG-SPEC--Operation-speculatively-executed--SVE-64-bit-non-contiguous-load--store--or-prefetch?lang=en#event_sve_ldst64_noncontig_spec) due to an SVE non-contiguous gather-load instruction with 64-bit vector elements in the address.
