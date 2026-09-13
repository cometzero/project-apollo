# ​0x8180, BR_UNCOND_RETIRED, Branch instruction architecturally executed, unconditional branch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8180--BR-UNCOND-RETIRED--Branch-instruction-architecturally-executed--unconditional-branch>

##### `0x8180`, BR\_UNCOND\_RETIRED, Branch instruction architecturally executed, unconditional branch

The counter counts each [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) counted by [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired) that is not counted by [BR\_COND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8181--BR-COND-RETIRED--Branch-instruction-architecturally-executed--conditional-branch?lang=en#event_br_cond_retired).

These are all unconditional branch instructions on the architecturally executed path.
