# ​0x80CA, LDST_SCALE_OPS_SPEC, Scalable load or store element operations speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CA--LDST-SCALE-OPS-SPEC--Scalable-load-or-store-element-operations-speculatively-executed>

##### `0x80CA`, LDST\_SCALE\_OPS\_SPEC, Scalable load or store element operations speculatively executed

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) or [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj) due to any of:

- An SVE vector load or store instruction other than a load and replicate instruction.
- An SME vector load or store instruction.

SVE non-vector load or store instructions and SVE vector load and replicate instructions are counted by the [LDST\_FIXED\_OPS\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CB--LDST-FIXED-OPS-SPEC--Non-scalable-load-or-store-element-operations-speculatively-executed?lang=en#event_ldst_fixed_ops_spec) event.

See [SIMD SVE and SME instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cachgccd) for information on the counter increment for different types of instruction.

The counter does not count tag loads or tag stores.
