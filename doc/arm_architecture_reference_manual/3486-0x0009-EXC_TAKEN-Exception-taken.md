# ​0x0009, EXC_TAKEN, Exception taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0009--EXC-TAKEN--Exception-taken>

##### `0x0009`, EXC\_TAKEN, Exception taken

The counter counts each exception taken.

It is IMPLEMENTATION SPECIFIC whether the counter counts each entry to Debug state.

> #### Note
>
> The counter counts the PE exceptions described in:
>
> - For exceptions taken to an Exception level using AArch64, Exception entry.
> - For exceptions taken to an Exception level using AArch32, [AArch32 state exception descriptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-17-AArch32-state-exception-descriptions?lang=en#beidfaic).

PMCEID0\_EL0[9] reads as 1 if this event is implemented and 0 otherwise.
