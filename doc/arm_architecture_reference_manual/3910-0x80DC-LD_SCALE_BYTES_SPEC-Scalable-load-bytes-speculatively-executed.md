# ​0x80DC, LD_SCALE_BYTES_SPEC, Scalable load bytes speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DC--LD-SCALE-BYTES-SPEC--Scalable-load-bytes-speculatively-executed>

##### `0x80DC`, LD\_SCALE\_BYTES\_SPEC, Scalable load bytes speculatively executed

The counter counts each speculatively read byte due to any of:

- An SVE vector load instruction other than a replicating `LD1R`, `LD1RQ`, or `LD1RO` instruction.
- An SME vector load instruction.

For each instruction, the counter is incremented by (16 ÷ (CSIZE ÷ MSIZE)), multiplied by the number of transferred vector registers.
