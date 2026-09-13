# ​Chapter G2 AArch32 Self-hosted Debug

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug>

### Chapter G2 AArch32 Self-hosted Debug

When the PE is using self-hosted debug, it generates *debug exceptions*. This chapter describes the AArch32 self-hosted debug Exception model. It is organized as follows:

- [About self-hosted debug](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-1-About-self-hosted-debug?lang=en#cegbebcc)
- [Routing debug exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-2-Routing-debug-exceptions?lang=en#beicggig)
- [The debug exception enable controls](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-3-The-debug-exception-enable-controls?lang=en#d3babdceee)
- [The effect of powerdown on debug exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-4-The-effect-of-powerdown-on-debug-exceptions?lang=en#beiggdia)
- [Summary of permitted routing and enabling of debug exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-5-Summary-of-permitted-routing-and-enabling-of-debug-exceptions?lang=en#beifhjhb)
- [Pseudocode description of debug exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-6-Pseudocode-description-of-debug-exceptions?lang=en#bcgebcjg)
- [Breakpoint Instruction exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-7-Breakpoint-Instruction-exceptions?lang=en#bgbdiaff)
- [Breakpoint exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-8-Breakpoint-exceptions?lang=en#bgbdjajb)
- [Watchpoint exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-9-Watchpoint-exceptions?lang=en#g3bcggecbj)
- [Vector Catch exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-10-Vector-Catch-exceptions?lang=en#g2bcgjgbcc)
- [Synchronization and debug exceptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-11-Synchronization-and-debug-exceptions?lang=en#g3bcgebfeb)
