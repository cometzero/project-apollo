# ​0x8110, BR_IMMED_PRED_RETIRED, Branch instruction architecturally executed, predicted immediate

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8110--BR-IMMED-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-immediate>

##### `0x8110`, BR\_IMMED\_PRED\_RETIRED, Branch instruction architecturally executed, predicted immediate

The counter counts each instruction counted by both [BR\_IMMED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000D--BR-IMMED-RETIRED--Branch-instruction-architecturally-executed--immediate?lang=en#event_br_immed_retired) and [BR\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811C--BR-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-branch?lang=en#event_br_pred_retired).

These are all direct branch instructions on the architecturally executed path, where the branch is correctly predicted.
