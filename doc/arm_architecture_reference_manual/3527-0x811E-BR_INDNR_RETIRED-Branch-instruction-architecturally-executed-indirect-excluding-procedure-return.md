# ​0x811E, BR_INDNR_RETIRED, Branch instruction architecturally executed, indirect excluding procedure return

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811E--BR-INDNR-RETIRED--Branch-instruction-architecturally-executed--indirect-excluding-procedure-return>

##### `0x811E`, BR\_INDNR\_RETIRED, Branch instruction architecturally executed, indirect excluding procedure return

The counter counts each instruction counted by [BR\_IND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811D--BR-IND-RETIRED--Instruction-architecturally-executed--indirect-branch?lang=en#event_br_ind_retired) that is not counted by [BR\_RETURN\_ANY\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810E--BR-RETURN-ANY-RETIRED--Branch-instruction-architecturally-executed--procedure-return?lang=en#event_br_return_any_retired).

These are all indirect branch instructions, excluding return instructions, on the architecturally executed path.
