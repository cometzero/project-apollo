# ​0x8108, BR_IMMED_TAKEN_RETIRED, Branch instruction architecturally executed, immediate, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8108--BR-IMMED-TAKEN-RETIRED--Branch-instruction-architecturally-executed--immediate--taken>

##### `0x8108`, BR\_IMMED\_TAKEN\_RETIRED, Branch instruction architecturally executed, immediate, taken

The counter counts each instruction counted by both [BR\_IMMED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000D--BR-IMMED-RETIRED--Branch-instruction-architecturally-executed--immediate?lang=en#event_br_immed_retired) and [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired).

These are all direct branch instructions on the architecturally executed path, where the branch is taken.
