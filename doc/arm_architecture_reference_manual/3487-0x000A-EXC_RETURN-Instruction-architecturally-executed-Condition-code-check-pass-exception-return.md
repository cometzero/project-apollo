# ​0x000A, EXC_RETURN, Instruction architecturally executed, Condition code check pass, exception return

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000A--EXC-RETURN--Instruction-architecturally-executed--Condition-code-check-pass--exception-return>

##### `0x000A`, EXC\_RETURN, Instruction architecturally executed, Condition code check pass, exception return

The counter counts each architecturally-executed exception return instruction.

Instructions defined in the following sections are counted as exception return instructions:

- For an exception return from an Exception level using AArch64, [Exception return](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-4-Exceptions/-D1-4-4-Exception-return?lang=en#beihbfcj).
- For an exception return from an Exception level using AArch32, [Exception return instructions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-15-Exception-return-to-an-Exception-level-using-AArch32/-G1-15-1-Exception-return-instructions?lang=en#beidcjac).

It is IMPLEMENTATION SPECIFIC whether the execution of an exception return instruction is counted if any of the following apply:

- Execution of the instruction is, itself, CONSTRAINED UNPREDICTABLE.
- Execution of an exception return instruction that generates an exception.
- Execution of the instruction sets [PSTATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-5-Process-state--PSTATE?lang=en#pstate).IL and does not generate an exception return.
- Exit from Debug state.

> #### Note
>
> - Examples of when an exception return instruction is CONSTRAINED UNPREDICTABLE are if the instruction is executed in AArch32 state at EL0 or in System mode.
> - A particular consequence of this CONSTRAINED UNPREDICTABLE behavior is that an implementation that does not support AArch32 state at EL1 or higher does not have to count AArch32 `MOVS PC, LR`, and related instructions, as exception return instructions.

PMCEID0\_EL0[10] reads as 1 if this event is implemented and 0 otherwise.
