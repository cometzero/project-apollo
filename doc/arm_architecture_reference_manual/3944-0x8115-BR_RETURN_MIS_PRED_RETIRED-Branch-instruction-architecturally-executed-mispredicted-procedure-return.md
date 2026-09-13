# ​0x8115, BR_RETURN_MIS_PRED_RETIRED, Branch instruction architecturally executed, mispredicted procedure return

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8115--BR-RETURN-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted-procedure-return>

##### `0x8115`, BR\_RETURN\_MIS\_PRED\_RETIRED, Branch instruction architecturally executed, mispredicted procedure return

The counter counts each instruction counted by [BR\_IND\_MIS\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8113--BR-IND-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted-indirect?lang=en#event_br_ind_mis_pred_retired) where if taken, the branch would also be counted by [BR\_RETURN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000E--BR-RETURN-RETIRED--Branch-instruction-architecturally-executed--procedure-return--taken?lang=en#event_br_return_retired).

These are all return instructions on the architecturally executed path, where the branch is mispredicted.
