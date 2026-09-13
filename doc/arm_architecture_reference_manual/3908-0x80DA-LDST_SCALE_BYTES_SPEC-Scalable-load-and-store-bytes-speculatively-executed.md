# ​0x80DA, LDST_SCALE_BYTES_SPEC, Scalable load and store bytes speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DA--LDST-SCALE-BYTES-SPEC--Scalable-load-and-store-bytes-speculatively-executed>

##### `0x80DA`, LDST\_SCALE\_BYTES\_SPEC, Scalable load and store bytes speculatively executed

The counter counts each byte speculatively read or written due to any of:

- An SVE vector load or store instruction other than a load and replicate instruction.
- An SME vector load or store instruction.

For each instruction, the counter is incremented by (16 ÷ (CSIZE ÷ MSIZE)), multiplied by the number of transferred vector registers.

SVE non-vector load or store instructions and SVE vector load and replicate instructions are counted by the [LDST\_FIXED\_BYTES\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DB--LDST-FIXED-BYTES-SPEC--Non-scalable-load-and-store-bytes-speculatively-executed?lang=en#event_ldst_fixed_bytes_spec) event.
