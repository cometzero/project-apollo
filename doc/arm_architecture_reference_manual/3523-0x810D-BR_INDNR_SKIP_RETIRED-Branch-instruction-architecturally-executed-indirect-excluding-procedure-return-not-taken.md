# ​0x810D, BR_INDNR_SKIP_RETIRED, Branch instruction architecturally executed, indirect excluding procedure return, not taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810D--BR-INDNR-SKIP-RETIRED--Branch-instruction-architecturally-executed--indirect-excluding-procedure-return--not-taken>

##### `0x810D`, BR\_INDNR\_SKIP\_RETIRED, Branch instruction architecturally executed, indirect excluding procedure return, not taken

The counter counts each instruction counted by both [BR\_INDNR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811E--BR-INDNR-RETIRED--Branch-instruction-architecturally-executed--indirect-excluding-procedure-return?lang=en#event_br_indnr_retired) and [BR\_SKIP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken?lang=en#event_br_skip_retired).

These are all indirect branch instructions, excluding return instructions, on the architecturally executed path, where the branch is not taken.
