# ​0x80CC, LD_SCALE_OPS_SPEC, Scalable load element operations speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CC--LD-SCALE-OPS-SPEC--Scalable-load-element-operations-speculatively-executed>

##### `0x80CC`, LD\_SCALE\_OPS\_SPEC, Scalable load element operations speculatively executed

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) counted by [LDST\_SCALE\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CA--LDST-SCALE-OPS-SPEC--Scalable-load-or-store-element-operations-speculatively-executed?lang=en#event_ldst_scale_ops_spec) due to any of:

- An SVE vector load instruction other than a replicating `LD1R`, `LD1RQ`, or `LD1RO` instruction.
- An SME vector load instruction.

See [SIMD SVE and SME instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cachgccd) for information on the counter increment for different types of instruction.

The counter does not count tag loads.
