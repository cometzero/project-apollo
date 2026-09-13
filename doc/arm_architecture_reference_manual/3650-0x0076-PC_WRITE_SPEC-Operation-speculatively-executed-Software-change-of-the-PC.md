# ​0x0076, PC_WRITE_SPEC, Operation speculatively executed, Software change of the PC

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0076--PC-WRITE-SPEC--Operation-speculatively-executed--Software-change-of-the-PC>

##### `0x0076`, PC\_WRITE\_SPEC, Operation speculatively executed, Software change of the PC

The counter counts each operation counted by [INST\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001B--INST-SPEC--Operation-speculatively-executed?lang=en#event_inst_spec) that is a [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji).

[Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) operations are defined by the [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired) event.

When FEAT\_PMUv3p8 is implemented, the counter counts the operation even if the branch is not taken. Otherwise, it is IMPLEMENTATION DEFINED whether the counter counts the operation when the branch is not taken.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
