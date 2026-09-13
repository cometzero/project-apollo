# ​0x000B, CID_WRITE_RETIRED, Instruction architecturally executed, Condition code check pass, write to CONTEXTIDR

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000B--CID-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--write-to-CONTEXTIDR>

##### `0x000B`, CID\_WRITE\_RETIRED, Instruction architecturally executed, Condition code check pass, write to CONTEXTIDR

The counter counts each `MSR` write to [CONTEXTIDR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-33-CONTEXTIDR-EL1--Context-ID-Register--EL1-?lang=en#reg_aarch64_contextidr_el1) and `MCR` write to [CONTEXTIDR](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G8-AArch32-System-Register-Descriptions/-G8-2-General-system-control-registers/-G8-2-28-CONTEXTIDR--Context-ID-Register?lang=en#reg_aarch32_contextidr).

If the PE performs two architecturally-executed writes to CONTEXTIDR without an intervening [Context synchronization event](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdjfhg), it is CONSTRAINED UNPREDICTABLE whether the first write is counted.

The counter counts only writes to these named registers. For example:

- When FEAT\_VHE or FEAT\_Debugv8p2 is implemented, the counter does not count writes using the register name [CONTEXTIDR\_EL2](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-34-CONTEXTIDR-EL2--Context-ID-Register--EL2-?lang=en#reg_aarch64_contextidr_el2).
- When FEAT\_VHE is implemented, the counter:
  - Counts each write using the register name [CONTEXTIDR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-33-CONTEXTIDR-EL1--Context-ID-Register--EL1-?lang=en#reg_aarch64_contextidr_el1), including when executing at EL2 and the Effective value of [HCR\_EL2](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-61-HCR-EL2--Hypervisor-Configuration-Register?lang=en#reg_aarch64_hcr_el2).E2H is 1.
  - Does not count writes using the register name CONTEXTIDR\_EL12.
- When FEAT\_NV2 is implemented, the counter counts writes using the register name [CONTEXTIDR\_EL1](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-33-CONTEXTIDR-EL1--Context-ID-Register--EL1-?lang=en#reg_aarch64_contextidr_el1), including when executing at EL1 and the Effective value of [HCR\_EL2](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-2-General-system-control-registers/-D24-2-61-HCR-EL2--Hypervisor-Configuration-Register?lang=en#reg_aarch64_hcr_el2).{NV2, NV1, NV} is {1, 1, 1}.

PMCEID0\_EL0[11] reads as 1 if this event is implemented and 0 otherwise.
