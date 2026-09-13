# ​0x001E, CHAIN, Chain a pair of event counters

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters>

##### `0x001E`, CHAIN, Chain a pair of event counters

Even-numbered counters never increment as a result of this event.

For an odd-numbered counter <n+1>, the counter increments when an event increments the preceding even-numbered counter <n> on the same PE causing unsigned overflow of bits [31:0] of the event counter <n>, and any of the following are true:

- FEAT\_PMUv3p5 is not implemented.
- EL2 is not implemented and PMCR.LP is 0.
- EL2 is implemented, <n> is less than the Effective value of HDCR.HPMN, and PMCR.LP is 0.
- EL2 is implemented, <n> is greater than or equal to the Effective value of HDCR.HPMN, and HDCR.HLP is 0.

This means the [CHAIN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters?lang=en#event_chain) event can be used to link the odd-numbered counter with the preceding even-numbered counter to provide a 64-bit counter.

If EL2 is implemented and <n+1> is equal to the Effective value of HDCR.HPMN, then it is UNPREDICTABLE whether the counter counts.

If FEAT\_PMUv3\_EXTPMN is implemented and <n+1> is equal to the Effective value of PMCCR.EPMN, then it is UNPREDICTABLE whether the counter counts.

> #### Note
>
> - When FEAT\_PMUv3p5 is not implemented, the [CHAIN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters?lang=en#event_chain) event allows software to use the N event counters as N 32-bit counters, N÷2 64-bit counters, or a mixture of 32-bit counters and 64-bit counters.
> - The [CHAIN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters?lang=en#event_chain) event only counts overflows from the preceding even-numbered counter on the same PE. This means it ignores the Effective value of [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0).MT.
> - The architecture does not provide atomic access to a pair of counters.

To filter the Exception levels and Security states in which the event is counted, software:

- Programs [PMEVTYPER<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0) to count the event in the required conditions.
- Programs [PMEVTYPER<n+1>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-12-PMEVTYPER-n--EL0--Performance-Monitors-Event-Type-Registers--n---0---30?lang=en#reg_aarch64_pmevtypern_el0) to count the [CHAIN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters?lang=en#event_chain) event in all Exception levels and states.

The PE might ignore the filter settings for the [CHAIN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters?lang=en#event_chain) event and behave as if they are set to count in all Exception levels and states. If software does not program the event in this way, the count becomes UNPREDICTABLE.

The architecture does not define the latency between the low counter overflowing and the high counter incrementing the [CHAIN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters?lang=en#event_chain) event. There is no requirement for updates to occur synchronously, but software reading or enabling the counter pair by reading the low counter first and the high counter second, with an intervening Context synchronization event, will not observe the low counter incrementing and overflowing for the event and the high counter not incrementing for the resulting [CHAIN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters?lang=en#event_chain) event. This means that the ISB executed after reading the low counter ensures the completion of the update of the high counter by the [CHAIN](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x001E--CHAIN--Chain-a-pair-of-event-counters?lang=en#event_chain) event.

PMCEID0\_EL0[30] reads as 1 if this event is implemented and 0 otherwise.
