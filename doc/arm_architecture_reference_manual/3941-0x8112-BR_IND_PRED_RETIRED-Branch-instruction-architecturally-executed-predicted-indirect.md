# ​0x8112, BR_IND_PRED_RETIRED, Branch instruction architecturally executed, predicted indirect

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8112--BR-IND-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-indirect>

##### `0x8112`, BR\_IND\_PRED\_RETIRED, Branch instruction architecturally executed, predicted indirect

The counter counts each instruction counted by both [BR\_IND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811D--BR-IND-RETIRED--Instruction-architecturally-executed--indirect-branch?lang=en#event_br_ind_retired) and [BR\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811C--BR-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-branch?lang=en#event_br_pred_retired).

These are all indirect branch instructions, including return instructions, on the architecturally executed path, where the branch is correctly predicted.
