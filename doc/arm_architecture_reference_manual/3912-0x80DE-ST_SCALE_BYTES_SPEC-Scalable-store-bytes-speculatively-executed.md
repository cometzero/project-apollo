# ​0x80DE, ST_SCALE_BYTES_SPEC, Scalable store bytes speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DE--ST-SCALE-BYTES-SPEC--Scalable-store-bytes-speculatively-executed>

##### `0x80DE`, ST\_SCALE\_BYTES\_SPEC, Scalable store bytes speculatively executed

The counter counts each speculatively written byte due to any of:

- An SVE vector store instruction.
- An SME vector store instruction.

For each instruction, the counter is incremented by (16 ÷ (CSIZE ÷ MSIZE)), multiplied by the number of transferred vector registers.
