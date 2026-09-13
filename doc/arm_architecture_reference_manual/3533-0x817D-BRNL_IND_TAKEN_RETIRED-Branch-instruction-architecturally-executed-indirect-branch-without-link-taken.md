# ​0x817D, BRNL_IND_TAKEN_RETIRED, Branch instruction architecturally executed, indirect branch without link, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x817D--BRNL-IND-TAKEN-RETIRED--Branch-instruction-architecturally-executed--indirect-branch-without-link--taken>

##### `0x817D`, BRNL\_IND\_TAKEN\_RETIRED, Branch instruction architecturally executed, indirect branch without link, taken

The counter counts each branch counted by both [BRNL\_TAKEN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x817B--BRNL-TAKEN-RETIRED--Branch-instruction-architecturally-executed--branch-without-link--taken?lang=en#event_brnl_taken_retired) and [BR\_IND\_TAKEN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810A--BR-IND-TAKEN-RETIRED--Branch-instruction-architecturally-executed--indirect--taken?lang=en#event_br_ind_taken_retired).

These are all indirect branch without link instructions on the architecturally executed path, where the branch is taken.
