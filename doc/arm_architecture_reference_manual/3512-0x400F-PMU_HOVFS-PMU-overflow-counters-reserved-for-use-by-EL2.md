# ​0x400F, PMU_HOVFS, PMU overflow, counters reserved for use by EL2

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x400F--PMU-HOVFS--PMU-overflow--counters-reserved-for-use-by-EL2>

##### `0x400F`, PMU\_HOVFS, PMU overflow, counters reserved for use by EL2

The counter counts each unsigned overflow of a PMU counter due to an event counted by an event counter <n> when all of the following are true:

- EL2 is implemented.
- [PMINTENSET\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-17-PMINTENSET-EL1--Performance-Monitors-Interrupt-Enable-Set-Register?lang=en#reg_aarch64_pmintenset_el1)[n] is 1.
- One of the following is true:
  - Counting the event causes unsigned overflow of [PMEVCNTR<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-10-PMEVCNTR-n--EL0--Performance-Monitors-Event-Count-Registers--n---0---30?lang=en#reg_aarch64_pmevcntrn_el0)[31:0], and either FEAT\_PMUv3p5 is not implemented or [MDCR\_EL2](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-3-Debug-System-registers/-D24-3-17-MDCR-EL2--Monitor-Debug-Configuration-Register--EL2-?lang=en#reg_aarch64_mdcr_el2).HLP is 0.
  - Counting the event causes unsigned overflow of [PMEVCNTR<n>\_EL0](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-5-Performance-Monitors-registers/-D24-5-10-PMEVCNTR-n--EL0--Performance-Monitors-Event-Count-Registers--n---0---30?lang=en#reg_aarch64_pmevcntrn_el0)[63:0], FEAT\_PMUv3p5 is implemented, and [MDCR\_EL2](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-3-Debug-System-registers/-D24-3-17-MDCR-EL2--Monitor-Debug-Configuration-Register--EL2-?lang=en#reg_aarch64_mdcr_el2).HLP is 1.
- The event counter <n> is in the second range.

The event is not transmitted to a trace unit if SelfHostedTraceEnabled() is TRUE and TRFCR\_EL2.E2TRE is 0.

> #### Note
>
> This is in addition to the rules for the export of all events to a trace unit. See [Controls to prohibit trace at Exception levels](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D3-AArch64-Self-hosted-Trace/-D3-2-Prohibited-regions-in-self-hosted-trace/-D3-2-1-Controls-to-prohibit-trace-at-Exception-levels?lang=en#babhgehg).

This event cannot be counted by the PMU. PMCEID0\_EL0[47] reads as 0.
