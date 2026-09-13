# ​0x0021, BR_RETIRED, Instruction architecturally executed, branch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch>

##### `0x0021`, BR\_RETIRED, Instruction architecturally executed, branch

The counter counts each branch instruction on the architecturally executed path that would incur cost if mispredicted.

If FEAT\_PMUv3p9 is implemented:

- Unconditional direct branch instructions are counted.
- Exception return instructions are counted.
- Exception-generating instructions are not counted.
- Context synchronization instructions are not counted.

If FEAT\_PMUv3p9 is not implemented, then it is IMPLEMENTATION DEFINED whether the counter increments for any of these instructions.

The counter counts all other branch instructions, [memory-reading instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions) and data-processing instructions that explicitly write to the PC, at retirement.

> #### Note
>
> Conditional branches are always counted, regardless of whether the branch is taken.

Arm recommends that [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired) counts Unconditional direct branch instructions and Exception return instructions.

From Armv8.6, if [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired) and [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired) are both implemented, the PE must treat the following types of instruction in the same way for both events:

- `BRK` and `BKPT` instructions.
- UNDEFINED instructions.
- The exception-generating instructions, `SVC`, `HVC`, and `SMC`.
- Context synchronization barrier instructions.

PMCEID1\_EL0[1] reads as 1 if this event is implemented and 0 otherwise.
