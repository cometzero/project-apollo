# ​0x810A, BR_IND_TAKEN_RETIRED, Branch instruction architecturally executed, indirect, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810A--BR-IND-TAKEN-RETIRED--Branch-instruction-architecturally-executed--indirect--taken>

##### `0x810A`, BR\_IND\_TAKEN\_RETIRED, Branch instruction architecturally executed, indirect, taken

The counter counts each instruction counted by both [BR\_IND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811D--BR-IND-RETIRED--Instruction-architecturally-executed--indirect-branch?lang=en#event_br_ind_retired) and [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired).

These are all indirect branch instructions, including return instructions, on the architecturally executed path, where the branch is taken.
