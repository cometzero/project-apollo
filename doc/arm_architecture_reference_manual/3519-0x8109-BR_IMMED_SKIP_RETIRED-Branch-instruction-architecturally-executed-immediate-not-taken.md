# ​0x8109, BR_IMMED_SKIP_RETIRED, Branch instruction architecturally executed, immediate, not taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8109--BR-IMMED-SKIP-RETIRED--Branch-instruction-architecturally-executed--immediate--not-taken>

##### `0x8109`, BR\_IMMED\_SKIP\_RETIRED, Branch instruction architecturally executed, immediate, not taken

The counter counts each instruction counted by both [BR\_IMMED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000D--BR-IMMED-RETIRED--Branch-instruction-architecturally-executed--immediate?lang=en#event_br_immed_retired) and [BR\_SKIP\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8107--BR-SKIP-RETIRED--Branch-instruction-architecturally-executed--not-taken?lang=en#event_br_skip_retired).

These are all direct branch instructions on the architecturally executed path, where the branch is not taken.
