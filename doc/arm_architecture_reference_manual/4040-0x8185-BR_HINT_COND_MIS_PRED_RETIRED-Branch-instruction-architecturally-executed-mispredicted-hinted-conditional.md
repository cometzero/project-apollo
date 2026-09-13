# ​0x8185, BR_HINT_COND_MIS_PRED_RETIRED, Branch instruction architecturally executed, mispredicted hinted conditional

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8185--BR-HINT-COND-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted-hinted-conditional>

##### `0x8185`, BR\_HINT\_COND\_MIS\_PRED\_RETIRED, Branch instruction architecturally executed, mispredicted hinted conditional

The counter counts each branch counted by both [BR\_HINT\_COND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8183--BR-HINT-COND-RETIRED--Branch-instruction-architecturally-executed--hinted-conditional?lang=en#event_br_hint_cond_retired) and [BR\_MIS\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0022--BR-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted?lang=en#event_br_mis_pred_retired).

These are all hinted conditional branch instructions on the architecturally executed path, where the branch is mispredicted.
