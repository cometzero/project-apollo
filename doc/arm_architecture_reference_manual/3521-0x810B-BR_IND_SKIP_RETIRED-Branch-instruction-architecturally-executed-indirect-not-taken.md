# ​0x810B, BR_IND_SKIP_RETIRED, Branch instruction architecturally executed, indirect, not taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810B--BR-IND-SKIP-RETIRED--Branch-instruction-architecturally-executed--indirect--not-taken>

##### `0x810B`, BR\_IND\_SKIP\_RETIRED, Branch instruction architecturally executed, indirect, not taken

The counter counts each instruction counted by both [BR\_IND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811D--BR-IND-RETIRED--Instruction-architecturally-executed--indirect-branch?lang=en#event_br_ind_retired) and [BR\_SKIP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken?lang=en#event_br_skip_retired).

These are all indirect branch instructions, including return instructions, on the architecturally executed path, where the branch is not taken.
