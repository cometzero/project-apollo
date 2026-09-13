# ​0x8056, SVE_SPEC, Operation speculatively executed, SVE data processing

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8056--SVE-SPEC--Operation-speculatively-executed--SVE-data-processing>

##### `0x8056`, SVE\_SPEC, Operation speculatively executed, SVE data processing

The counter counts each operation counted by [ASE\_SVE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8057--ASE-SVE-SPEC--Operation-speculatively-executed--Advanced-SIMD-data-processing-or-SVE-data-processing?lang=en#event_ase_sve_spec) that is an SVE data-processing operation.

An SVE data-processing operation is any operation due to an instruction that operates on the SVE scalable vector and predicate registers that is not any of the following:

- A load or store operation. These are counted by [SVE\_INST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8006--SVE-INST-SPEC--Operation-speculatively-executed--SVE?lang=en#event_sve_inst_spec).
- If the Cryptographic Extension is implemented, an operation counted by [CRYPTO\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0077--CRYPTO-SPEC--Operation-speculatively-executed--cryptographic-data-processing?lang=en#event_crypto_spec) as a Cryptographic data-processing operation.
- When FEAT\_SME is implemented, an operation counted by [SME\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x835C--SME-SPEC--Operation-speculatively-executed--SME-data-processing?lang=en#event_sme_spec) as an SME data-processing operation.

If the Cryptographic Extension and FEAT\_SVE2 are implemented, operations due to the SVE `PMULLB` and `PMULLT` (Q variants) instructions are not counted by [CRYPTO\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0077--CRYPTO-SPEC--Operation-speculatively-executed--cryptographic-data-processing?lang=en#event_crypto_spec) and are counted as SVE data-processing operations.

Operations due to data-processing instructions defined by FEAT\_SME which involve the SVE registers but do not involve any ZA or ZT registers are counted as SVE data-processing operations.
