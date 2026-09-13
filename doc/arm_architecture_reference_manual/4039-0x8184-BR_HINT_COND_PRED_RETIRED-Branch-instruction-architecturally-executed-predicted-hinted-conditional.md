# ​0x8184, BR_HINT_COND_PRED_RETIRED, Branch instruction architecturally executed, predicted hinted conditional

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8184--BR-HINT-COND-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-hinted-conditional>

##### `0x8184`, BR\_HINT\_COND\_PRED\_RETIRED, Branch instruction architecturally executed, predicted hinted conditional

The counter counts each branch counted by both [BR\_HINT\_COND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8183--BR-HINT-COND-RETIRED--Branch-instruction-architecturally-executed--hinted-conditional?lang=en#event_br_hint_cond_retired) and [BR\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811C--BR-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-branch?lang=en#event_br_pred_retired).

These are all hinted conditional branch instructions on the architecturally executed path, where the branch is correctly predicted.
