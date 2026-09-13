# ​0x80DB, LDST_FIXED_BYTES_SPEC, Non-scalable load and store bytes speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80DB--LDST-FIXED-BYTES-SPEC--Non-scalable-load-and-store-bytes-speculatively-executed>

##### `0x80DB`, LDST\_FIXED\_BYTES\_SPEC, Non-scalable load and store bytes speculatively executed

The counter counts each byte speculatively read or written due to any of:

- Any load, store, or atomic operation, other than loads and stores of the SVE P and Z registers, and the SME ZA registers.
- Any SVE non-vector load or store operation.
- An SVE load and replicate instruction, including: `LD1R`, `LD1RB`, `LD1RD`, `LD1RH`, `LD1RO`, `LD1ROB`, `LD1ROD`, `LD1ROH`, `LD1ROW`, `LD1RQ`, `LD1RQB`, `LD1RQD`, `LD1RQH`, `LD1RQW`, `LD1RSB`, `LD1RSH`, or `LD1RSW`.

For each instruction, the counter is incremented by the number of bytes transferred per register multiplied by the number of registers transferred multiplied by the number of transfers made per register. For example, the counter counts bytes as follows:

- Load and store of a single register instructions, other than SVE and SME vector loads and stores, increment the counter by (MSIZE ÷ 8).
- Load and store of a pair of registers instructions, other than SVE and SME vector loads and stores, increment the counter by 2 × (MSIZE ÷ 8).
- AArch32 load and store multiple registers instructions increment the counter by the number of registers transferred multiplied by (MSIZE ÷ 8).
- Atomic store instructions increment the counter by (MSIZE ÷ 8). These are instructions that atomically update a value in memory without returning a value to a register.
- Atomic load, compare and swap of a single register, and swap instructions increment the counter by 2 × (MSIZE ÷ 8). Atomic load instructions are instructions that atomically update a value in memory, returning a value to a register.
- Compare and swap of a pair of registers increment the counter by 4 × (MSIZE ÷ 8).
- SVE and Advanced SIMD `LD1R` instructions increment the counter by (MSIZE ÷ 8).
- SVE `LD1RQ` instructions increment the counter by 16.
- SVE `LD1RO` instructions increment the counter by 32.
- Advanced SIMD `LD[1-4]` and `ST[1-4]` instructions increment the counter by the number of registers transferred multiplied by the number of bytes being transferred per register.
- `DC ZVA` and `DC GZVA` instructions increment by the counter by 2(DCZID\_EL0.BS).
- `LDR` (table) and `STR` (table) instructions increment the counter by 64.
- `LD64B` and `ST64B` increment the counter by 64.
