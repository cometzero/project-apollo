# ​0x8183, BR_HINT_COND_RETIRED, Branch instruction architecturally executed, hinted conditional

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8183--BR-HINT-COND-RETIRED--Branch-instruction-architecturally-executed--hinted-conditional>

##### `0x8183`, BR\_HINT\_COND\_RETIRED, Branch instruction architecturally executed, hinted conditional

The counter counts each branch counted by [BR\_COND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8181--BR-COND-RETIRED--Branch-instruction-architecturally-executed--conditional-branch?lang=en#event_br_cond_retired) that is a hinted conditional branch.

These are all hinted conditional branch instructions on the architecturally executed path.

The hinted conditional branch instruction is `BC.cond`.
