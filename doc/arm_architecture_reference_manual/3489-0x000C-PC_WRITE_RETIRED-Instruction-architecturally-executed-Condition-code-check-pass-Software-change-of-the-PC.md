# ​0x000C, PC_WRITE_RETIRED, Instruction architecturally executed, Condition code check pass, Software change of the PC

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC>

##### `0x000C`, PC\_WRITE\_RETIRED, Instruction architecturally executed, Condition code check pass, Software change of the PC

The counter counts each architecturally-executed [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) that is taken.

This includes all:

- Branch instructions.
- [Memory-reading instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions) that explicitly write to the PC.
- Data-processing instructions that explicitly write to the PC.
- Exception return instructions.

> #### Note
>
> Conditional branches are only counted if the branch is taken.

If FEAT\_PMUv3p9 is implemented, then the following instructions are not included as a [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji):

- A `BRK` or `BKPT` instruction.
- An UNDEFINED instruction that generates an exception.
- An exception-generating instruction, `SVC`, `HVC`, or `SMC`, that generates an exception.
- A Context synchronization barrier instruction, `ISB`.

If FEAT\_PMUv3p9 is not implemented, then it is IMPLEMENTATION DEFINED whether any of these instructions are included as a [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji).

The counter does not increment for exceptions other than those explicitly identified in these lists.

If [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired) and [BR\_SKIP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken?lang=en#event_br_skip_retired) are both implemented, the PE must treat the following types of instruction in the same way for both events:

- `BRK` and `BKPT` instructions.
- UNDEFINED instructions.
- The exception-generating instructions, `SVC`, `HVC`, and `SMC`.
- Context synchronization barrier instructions.

From Armv8.6, if [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired) is also implemented, the PE must also treat these types of instruction in the same way for the [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired), [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired), and [BR\_SKIP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken?lang=en#event_br_skip_retired) events.

PMCEID0\_EL0[12] reads as 1 if this event is implemented and 0 otherwise.
