# ​0x80CE, ST_SCALE_OPS_SPEC, Scalable store element operations speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CE--ST-SCALE-OPS-SPEC--Scalable-store-element-operations-speculatively-executed>

##### `0x80CE`, ST\_SCALE\_OPS\_SPEC, Scalable store element operations speculatively executed

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj) counted by [LDST\_SCALE\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CA--LDST-SCALE-OPS-SPEC--Scalable-load-or-store-element-operations-speculatively-executed?lang=en#event_ldst_scale_ops_spec) due to any of:

- An SVE predicated vector store instruction.
- An SME vector store instruction.

See [SIMD SVE and SME instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cachgccd) for information on the counter increment for different types of instruction.

The counter does not count tag stores.
