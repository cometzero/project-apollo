# ​0x8179, BRNL_INDNR_TAKEN_RETIRED, Branch instruction architecturally executed, indirect branch without link excluding procedure return, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8179--BRNL-INDNR-TAKEN-RETIRED--Branch-instruction-architecturally-executed--indirect-branch-without-link-excluding-procedure-return--taken>

##### `0x8179`, BRNL\_INDNR\_TAKEN\_RETIRED, Branch instruction architecturally executed, indirect branch without link excluding procedure return, taken

The counter counts each branch counted by [BRNL\_IND\_TAKEN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x817D--BRNL-IND-TAKEN-RETIRED--Branch-instruction-architecturally-executed--indirect-branch-without-link--taken?lang=en#event_brnl_ind_taken_retired) that is not counted by [BR\_RETURN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000E--BR-RETURN-RETIRED--Branch-instruction-architecturally-executed--procedure-return--taken?lang=en#event_br_return_retired).

These are all indirect branch without link excluding procedure return instructions on the architecturally executed path, where the branch is taken.
