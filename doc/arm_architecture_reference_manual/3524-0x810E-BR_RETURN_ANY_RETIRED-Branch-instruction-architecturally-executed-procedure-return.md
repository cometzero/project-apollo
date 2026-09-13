# ​0x810E, BR_RETURN_ANY_RETIRED, Branch instruction architecturally executed, procedure return

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810E--BR-RETURN-ANY-RETIRED--Branch-instruction-architecturally-executed--procedure-return>

##### `0x810E`, BR\_RETURN\_ANY\_RETIRED, Branch instruction architecturally executed, procedure return

The counter counts each instruction counted by [BR\_IND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811D--BR-IND-RETIRED--Instruction-architecturally-executed--indirect-branch?lang=en#event_br_ind_retired) where if taken, the branch would be counted by [BR\_RETURN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000E--BR-RETURN-RETIRED--Branch-instruction-architecturally-executed--procedure-return--taken?lang=en#event_br_return_retired).

These are all return instructions on the architecturally executed path.
