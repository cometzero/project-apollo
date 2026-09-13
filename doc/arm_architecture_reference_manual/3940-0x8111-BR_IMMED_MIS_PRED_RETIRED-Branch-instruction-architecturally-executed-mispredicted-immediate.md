# ​0x8111, BR_IMMED_MIS_PRED_RETIRED, Branch instruction architecturally executed, mispredicted immediate

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8111--BR-IMMED-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted-immediate>

##### `0x8111`, BR\_IMMED\_MIS\_PRED\_RETIRED, Branch instruction architecturally executed, mispredicted immediate

The counter counts each instruction counted by both [BR\_IMMED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000D--BR-IMMED-RETIRED--Branch-instruction-architecturally-executed--immediate?lang=en#event_br_immed_retired) and [BR\_MIS\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0022--BR-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted?lang=en#event_br_mis_pred_retired).

These are all direct branch instructions on the architecturally executed path, where the branch is mispredicted.
