# ​0x8107, BR_SKIP_RETIRED, Branch instruction architecturally executed, not taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken>

##### `0x8107`, BR\_SKIP\_RETIRED, Branch instruction architecturally executed, not taken

The counter counts each conditional [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) instruction that is not taken.

This includes all:

- Conditional branch instructions.
- Conditional [memory-reading instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions) that explicitly write to the PC.
- Conditional data-processing instructions that explicitly write to the PC.
- Conditional exception return instructions.

These are the same instructions which, if unconditional, or conditional and taken, are counted by the [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired) event.

If FEAT\_PMUv3p9 is implemented, then the following instructions are not included as a [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji):

- A conditional UNDEFINED instruction that does not generate an exception.
- A conditional exception-generating instruction, `SVC`, `HVC`, or `SMC`, that does not generate an exception.
- A conditional Context synchronization barrier instruction, `ISB`, that fails its condition code check.

If FEAT\_PMUv3p9 is not implemented, then it is IMPLEMENTATION DEFINED whether these instructions are included as a [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji).

> #### Note
>
> Many of these instructions can only be conditional in the AArch32 instruction sets.

The counter does not increment for exceptions other than those explicitly identified in these lists.

If [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired) and [BR\_SKIP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken?lang=en#event_br_skip_retired) are both implemented, the PE must treat the following types of instruction in the same way for both events:

- `BRK` and `BKPT` instructions.
- UNDEFINED instructions.
- The exception-generating instructions, `SVC`, `HVC`, and `SMC`.
- Context synchronization barrier instructions.

From Armv8.6, if [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired) is also implemented, the PE must also treat these types of instruction in the same way for the [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired) event.
