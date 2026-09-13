# ​0x811A, BR_SKIP_PRED_RETIRED, Branch instruction architecturally executed, predicted branch, not taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811A--BR-SKIP-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-branch--not-taken>

##### `0x811A`, BR\_SKIP\_PRED\_RETIRED, Branch instruction architecturally executed, predicted branch, not taken

The counter counts each instruction counted by both [BR\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811C--BR-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-branch?lang=en#event_br_pred_retired) and [BR\_SKIP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken?lang=en#event_br_skip_retired).

These are all branch instructions on the architecturally executed path, where the branch is correctly predicted and not taken.
