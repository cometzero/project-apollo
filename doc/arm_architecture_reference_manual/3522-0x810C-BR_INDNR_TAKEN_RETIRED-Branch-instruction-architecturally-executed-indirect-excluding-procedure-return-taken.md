# ​0x810C, BR_INDNR_TAKEN_RETIRED, Branch instruction architecturally executed, indirect excluding procedure return, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810C--BR-INDNR-TAKEN-RETIRED--Branch-instruction-architecturally-executed--indirect-excluding-procedure-return--taken>

##### `0x810C`, BR\_INDNR\_TAKEN\_RETIRED, Branch instruction architecturally executed, indirect excluding procedure return, taken

The counter counts each instruction counted by both [BR\_IND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811D--BR-IND-RETIRED--Instruction-architecturally-executed--indirect-branch?lang=en#event_br_ind_retired) and [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired), that is not counted by [BR\_RETURN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000E--BR-RETURN-RETIRED--Branch-instruction-architecturally-executed--procedure-return--taken?lang=en#event_br_return_retired).

These are all indirect branch instructions, excluding return instructions, on the architecturally executed path, where the branch is taken.
