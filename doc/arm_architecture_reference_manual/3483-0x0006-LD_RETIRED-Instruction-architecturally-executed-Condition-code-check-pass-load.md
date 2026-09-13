# ​0x0006, LD_RETIRED, Instruction architecturally executed, Condition code check pass, load

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0006--LD-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--load>

##### `0x0006`, LD\_RETIRED, Instruction architecturally executed, Condition code check pass, load

The counter counts each architecturally-executed [memory-reading instruction](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#pmudef_memory_reading_instructions) counted by [INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed?lang=en#event_inst_retired).

It is IMPLEMENTATION DEFINED whether the prefetch instructions counted by [PRF\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82B3--PRF-RETIRED--Instruction-architecturally-executed--prefetch?lang=en#event_prf_retired) are counted as Memory-reading instructions:

- If the prefetch instructions are counted as Memory-reading instructions, then they are counted by [LD\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0006--LD-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--load?lang=en#event_ld_retired) and [LD\_ANY\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82A8--LD-ANY-RETIRED--Instruction-architecturally-executed--load?lang=en#event_ld_any_retired).
- Otherwise, if the prefetch instructions are not counted as Memory-reading instructions by [LD\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0006--LD-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--load?lang=en#event_ld_retired), then it is further IMPLEMENTATION DEFINED which one of the following applies:
  - They are counted as data-processing instructions.
  - They are counted by [LDST\_ANY\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82AA--LDST-ANY-RETIRED--Instruction-architecturally-executed--load-or-store?lang=en#event_ldst_any_retired).

Arm recommends that if a prefetch instruction is not implemented as a NOP and the [PRF\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82B3--PRF-RETIRED--Instruction-architecturally-executed--prefetch?lang=en#event_prf_retired) event is not implemented, then the instruction is counted as a Memory-reading instruction.

PMCEID0\_EL0[6] reads as 1 if this event is implemented and 0 otherwise.
