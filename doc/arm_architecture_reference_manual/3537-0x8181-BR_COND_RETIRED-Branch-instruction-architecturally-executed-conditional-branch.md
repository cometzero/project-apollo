# ​0x8181, BR_COND_RETIRED, Branch instruction architecturally executed, conditional branch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8181--BR-COND-RETIRED--Branch-instruction-architecturally-executed--conditional-branch>

##### `0x8181`, BR\_COND\_RETIRED, Branch instruction architecturally executed, conditional branch

The counter counts each [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) counted by [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired) that is a conditional branch.

These are all conditional branch instructions on the architecturally executed path.

In the A64 instruction set, conditional branches are:

- `B.cond`, `CBNZ`, `CBZ`, `TBNZ`, and `TBZ`.
- If FEAT\_HBC is implemented, `BC.cond`.
- If FEAT\_CMPBR is implemented, `CB<cc>`, `CBB<cc>`, and `CBH<cc>`.

This includes conditional branch instructions with the `AL` or `NV` condition code.

In the A32 instruction set, conditional branches are [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) instructions that have bits [31:29] of the instruction opcode not equal to `0b111`.

In the T32 instruction set, conditional branches are `B<c>`, `B<c>.W`, [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) instructions executed in an IT block, `CBNZ`, and `CBZ`. Branch instruction encodings, including `B{<c>}` and `B{<c>}.W`, where `<c>` is either omitted or `AL` are only considered conditional branches when they are the last instruction in an IT block.
