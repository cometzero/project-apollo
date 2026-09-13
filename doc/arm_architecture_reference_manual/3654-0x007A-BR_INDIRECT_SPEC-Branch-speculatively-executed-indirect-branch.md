# ​0x007A, BR_INDIRECT_SPEC, Branch speculatively executed, indirect branch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x007A--BR-INDIRECT-SPEC--Branch-speculatively-executed--indirect-branch>

##### `0x007A`, BR\_INDIRECT\_SPEC, Branch speculatively executed, indirect branch

The counter counts each [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) indirect branch instruction.

Indirect branch instructions are [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) instructions other than exception-generating instructions and immediate branch instructions. [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) has the same definition as for the [PC\_WRITE\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0076--PC-WRITE-SPEC--Operation-speculatively-executed--Software-change-of-the-PC?lang=en#event_pc_write_spec) event. Immediate branch instructions are defined by the [BR\_IMMED\_SPEC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0078--BR-IMMED-SPEC--Branch-speculatively-executed--immediate-branch?lang=en#event_br_immed_spec) event.

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
