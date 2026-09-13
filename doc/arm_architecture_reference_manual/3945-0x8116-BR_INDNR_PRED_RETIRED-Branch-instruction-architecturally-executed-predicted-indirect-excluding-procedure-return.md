# ​0x8116, BR_INDNR_PRED_RETIRED, Branch instruction architecturally executed, predicted indirect excluding procedure return

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8116--BR-INDNR-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-indirect-excluding-procedure-return>

##### `0x8116`, BR\_INDNR\_PRED\_RETIRED, Branch instruction architecturally executed, predicted indirect excluding procedure return

The counter counts each instruction counted by [BR\_IND\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8112--BR-IND-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-indirect?lang=en#event_br_ind_pred_retired) where if taken, the branch would not be counted by [BR\_RETURN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000E--BR-RETURN-RETIRED--Branch-instruction-architecturally-executed--procedure-return--taken?lang=en#event_br_return_retired).

These are all indirect branch instructions, excluding return instructions, on the architecturally executed path, where the branch is correctly predicted.
