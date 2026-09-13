# ​0x810F, BR_RETURN_SKIP_RETIRED, Branch instruction architecturally executed, procedure return, not taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810F--BR-RETURN-SKIP-RETIRED--Branch-instruction-architecturally-executed--procedure-return--not-taken>

##### `0x810F`, BR\_RETURN\_SKIP\_RETIRED, Branch instruction architecturally executed, procedure return, not taken

The counter counts each instruction counted by both [BR\_RETURN\_ANY\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x810E--BR-RETURN-ANY-RETIRED--Branch-instruction-architecturally-executed--procedure-return?lang=en#event_br_return_any_retired) and [BR\_SKIP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken?lang=en#event_br_skip_retired).

These are all return instructions on the architecturally executed path, where the branch is not taken.
