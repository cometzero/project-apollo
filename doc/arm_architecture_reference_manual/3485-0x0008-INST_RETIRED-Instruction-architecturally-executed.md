# ​0x0008, INST_RETIRED, Instruction architecturally executed

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed>

##### `0x0008`, INST\_RETIRED, Instruction architecturally executed

The counter counts each architecturally-executed instruction.

If FEAT\_PMUv3p9 is implemented, then the counter counts architecturally-executed `MOVPRFX` instructions.

Otherwise, it is IMPLEMENTATION DEFINED whether the counter counts architecturally-executed `MOVPRFX` instructions.

PMCEID0\_EL0[8] reads as 1 if this event is implemented and 0 otherwise.
