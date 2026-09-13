# ​0x80CB, LDST_FIXED_OPS_SPEC, Non-scalable load or store element operations speculatively executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x80CB--LDST-FIXED-OPS-SPEC--Non-scalable-load-or-store-element-operations-speculatively-executed>

##### `0x80CB`, LDST\_FIXED\_OPS\_SPEC, Non-scalable load or store element operations speculatively executed

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) or [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj) due to any of:

- Any load, store, or atomic operation, other than loads and stores of the SVE P and Z registers, and the SME ZA registers.
- Any SVE non-vector load or store operation.
- An SVE load and replicate instruction, including: `LD1R`, `LD1RB`, `LD1RD`, `LD1RH`, `LD1RO`, `LD1ROB`, `LD1ROD`, `LD1ROH`, `LD1ROW`, `LD1RQ`, `LD1RQB`, `LD1RQD`, `LD1RQH`, `LD1RQW`, `LD1RSB`, `LD1RSH`, or `LD1RSW`.

For each instruction, the counter is incremented by the number of operations specified by the instruction. For example, the counter counts operations as follows:

- Load and store of a single register instructions, other than SVE and SME vector loads and stores, increment the counter by 1.
- Load and store of a pair of registers instructions, other than SVE and SME vector loads and stores, increment the counter by 2.
- AArch32 load and store multiple registers instructions increment the counter by the number of registers transferred.
- Atomic store instructions increment the counter by 1. These are instructions that atomically update a value in memory without returning a value to a register.
- Atomic load, compare and swap of a single register, and swap instructions increment the counter by 2. Atomic load instructions are instructions that atomically update a value in memory, returning a value to a register.
- Compare and swap of a pair of registers increment the counter by 4.
- SVE and Advanced SIMD `LD1R` instructions increment the counter by 1.
- SVE `LD1RQ` instructions increment the counter by (128 ÷ CSIZE).
- SVE `LD1RO` instructions increment the counter by (256 ÷ CSIZE).
- Advanced SIMD `LD[1-4]` and `ST[1-4]` instructions increment the counter by the number of elements transferred per vector multiplied by the number of transferred registers.
- `DC ZVA` and `DC GZVA` instructions increment by an IMPLEMENTATION DEFINED amount.
- `LDR` (table) and `STR` (table) instructions increment the counter by 1.
- `LD64B` and `ST64B` increment the counter by 8.

> #### Note
>
> When a replicating load instruction loads data of the same size as the vector length, which causes no replication to occur, the instruction is counted.
