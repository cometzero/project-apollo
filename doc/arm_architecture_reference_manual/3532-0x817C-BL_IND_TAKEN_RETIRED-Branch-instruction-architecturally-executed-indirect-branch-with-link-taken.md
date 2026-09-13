# ​0x817C, BL_IND_TAKEN_RETIRED, Branch instruction architecturally executed, indirect branch with link, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x817C--BL-IND-TAKEN-RETIRED--Branch-instruction-architecturally-executed--indirect-branch-with-link--taken>

##### `0x817C`, BL\_IND\_TAKEN\_RETIRED, Branch instruction architecturally executed, indirect branch with link, taken

The counter counts each branch counted by both [BL\_TAKEN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x817A--BL-TAKEN-RETIRED--Branch-instruction-architecturally-executed--branch-with-link--taken?lang=en#event_bl_taken_retired) and [BR\_IND\_TAKEN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810A--BR-IND-TAKEN-RETIRED--Branch-instruction-architecturally-executed--indirect--taken?lang=en#event_br_ind_taken_retired).

These are all indirect branch with link instructions on the architecturally executed path, where the branch is taken.
