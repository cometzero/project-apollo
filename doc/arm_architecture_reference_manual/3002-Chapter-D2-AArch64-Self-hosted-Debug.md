# ​Chapter D2 AArch64 Self-hosted Debug

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug>

### Chapter D2 AArch64 Self-hosted Debug

When the PE is using self-hosted debug, it generates *debug exceptions*. This chapter describes the AArch64 self-hosted debug Exception model. It is organized as follows:

- [About self-hosted debug](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-1-About-self-hosted-debug?lang=en#ceggbihe)
- [Routing debug exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-2-Routing-debug-exceptions?lang=en#d2beicggig)
- [The debug exception enable controls](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-3-The-debug-exception-enable-controls?lang=en#babdceee)
- [The effect of powerdown on debug exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-4-The-effect-of-powerdown-on-debug-exceptions?lang=en#d2beiggdia)
- [Summary of the routing and enabling of debug exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-5-Summary-of-the-routing-and-enabling-of-debug-exceptions?lang=en#d2beifhjhb)
- [Pseudocode description of debug exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-6-Pseudocode-description-of-debug-exceptions?lang=en#d2bcgebcjg)
- [Breakpoint Instruction exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-7-Breakpoint-Instruction-exceptions?lang=en#bcgiehag)
- [Breakpoint exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-8-Breakpoint-exceptions?lang=en#bcggeabj)
- [Watchpoint exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-9-Watchpoint-exceptions?lang=en#bcggecbj)
- [Vector Catch exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-10-Vector-Catch-exceptions?lang=en#bcgjgbcc)
- [Software Step exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-11-Software-Step-exceptions?lang=en#bcgiidaj)
- [Synchronization and debug exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-12-Synchronization-and-debug-exceptions?lang=en#bcgebfeb)
