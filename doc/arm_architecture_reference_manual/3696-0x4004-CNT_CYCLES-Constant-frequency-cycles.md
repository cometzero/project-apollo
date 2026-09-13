# ​0x4004, CNT_CYCLES, Constant frequency cycles

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4004--CNT-CYCLES--Constant-frequency-cycles>

##### `0x4004`, CNT\_CYCLES, Constant frequency cycles

The counter increments at a constant frequency when the PE is not in `WFI` or `WFE` state, equal to the rate of increment of the System Counter, [CNTPCT\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-10-Generic-Timer-registers/-D24-10-17-CNTPCT-EL0--Counter-timer-Physical-Count-Register?lang=en#reg_aarch64_cntpct_el0).

When the PE is in `WFI` or `WFE` state:

- If FEAT\_PMUv3p9 is implemented, then the counter does not count.
- Otherwise, it is IMPLEMENTATION SPECIFIC whether the counter counts.

PMCEID0\_EL0[36] reads as 1 if this event is implemented and 0 otherwise.
