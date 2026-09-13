# ​0x0078, BR_IMMED_SPEC, Branch speculatively executed, immediate branch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0078--BR-IMMED-SPEC--Branch-speculatively-executed--immediate-branch>

##### `0x0078`, BR\_IMMED\_SPEC, Branch speculatively executed, immediate branch

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) immediate branch instruction.

Operations due to the following instructions are counted as [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) immediate branch instructions:

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

If the Context synchronization barrier instruction ISB is counted as a [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) instruction by [PC\_WRITE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0076--PC-WRITE-SPEC--Operation-speculatively-executed--Software-change-of-the-PC?lang=en#event_pc_write_spec), then it is IMPLEMENTATION DEFINED whether ISB is counted as a [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) immediate branch instruction.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
