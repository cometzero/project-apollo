# ​0x000D, BR_IMMED_RETIRED, Branch instruction architecturally executed, immediate

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000D--BR-IMMED-RETIRED--Branch-instruction-architecturally-executed--immediate>

##### `0x000D`, BR\_IMMED\_RETIRED, Branch instruction architecturally executed, immediate

The counter counts each architecturally-executed immediate branch instruction.

The following instructions are counted as immediate branch instructions:

- For AArch32 state, the following instructions:
  - `B{<c>} <label>`.
  - `BL{<c>} <label>`.
  - `BLX{<c>} <label>`.
  - `CBZ <Rn>, <label>`.
  - `CBNZ <label>`.
- For AArch64 state, the following instructions:
  - `B <label>`.
  - `B.cond <label>`.
  - `BL <label>`.
  - `CBZ <Rn>, <label>`.
  - `CBNZ <Rn>, <label>`.
  - `TBZ <Rn>, <label>`.
  - `TBNZ <Rn>, <label>`.
  - `BC.cond <label>`.
  - `CB<cc> <Rn>, #<imm>, <label>`.
  - `CB<cc> <Rn>, #<Rm>, <label>`.
  - `CBB<cc> <Rn>, #<Rm>, <label>`.
  - `CBH<cc> <Rn>, #<Rm>, <label>`.

> #### Note
>
> Conditional branches are always counted, regardless of whether the branch is taken or not taken.

If the Context synchronization barrier instruction ISB is counted as a [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) instruction by [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired), then it is IMPLEMENTATION DEFINED whether ISB is counted as an immediate branch instruction.

PMCEID0\_EL0[13] reads as 1 if this event is implemented and 0 otherwise.
