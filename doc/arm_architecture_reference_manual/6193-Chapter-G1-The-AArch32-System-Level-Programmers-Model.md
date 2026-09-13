# ​Chapter G1 The AArch32 System Level Programmers’ Model

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model>

### Chapter G1 The AArch32 System Level Programmers’ Model

This chapter gives a system level description of the programmers’ model for execution in AArch32 state. It contains the following sections:

- [About the AArch32 System level programmers’ model](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-1-About-the-AArch32-System-level-programmers--model?lang=en#cihiacda)
- [Exception levels](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-2-Exception-levels?lang=en#g1beiegadj)
- [Exception terminology](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-3-Exception-terminology?lang=en#g1beihgdhd)
- [Execution state](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-4-Execution-state?lang=en#g1beihghcc)
- [Instruction Set state](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-5-Instruction-Set-state?lang=en#chdfgbfc)
- [Security state](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-6-Security-state?lang=en#g1beibjggi)
- [Security state, Exception levels, and AArch32 execution privilege](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-7-Security-state--Exception-levels--and-AArch32-execution-privilege?lang=en#chdfhajj)
- [Virtualization](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-8-Virtualization?lang=en#g1beibcfbg)
- [AArch32 state PE modes](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-9-AArch32-state-PE-modes?lang=en#cihbgjdi)
- [AArch32 general-purpose registers, the PC, and the Special-purpose registers](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-10-AArch32-general-purpose-registers--the-PC--and-the-Special-purpose-registers?lang=en#chdceeeed0)
- [Process state, PSTATE](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-11-Process-state--PSTATE?lang=en#chdedfdc)
- [Instruction set states](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-12-Instruction-set-states?lang=en#zeibjecj)
- [Handling exceptions that are taken to an Exception level using AArch32](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-13-Handling-exceptions-that-are-taken-to-an-Exception-level-using-AArch32?lang=en#cihgiebj)
- [Routing of aborts taken to AArch32 state](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-14-Routing-of-aborts-taken-to-AArch32-state?lang=en#beijfcaf)
- [Exception return to an Exception level using AArch32](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-15-Exception-return-to-an-Exception-level-using-AArch32?lang=en#cihbafec)
- [Asynchronous exception behavior for exceptions taken from AArch32 state](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-16-Asynchronous-exception-behavior-for-exceptions-taken-from-AArch32-state?lang=en#beighjbc)
- [AArch32 state exception descriptions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-17-AArch32-state-exception-descriptions?lang=en#beidfaic)
- [Reset into AArch32 state](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-18-Reset-into-AArch32-state?lang=en#cihhahcg)
- [Mechanisms for entering a low-power state](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-19-Mechanisms-for-entering-a-low-power-state?lang=en#chdbefdc)
- [The AArch32 System register interface](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-20-The-AArch32-System-register-interface?lang=en#zeibehhd)
- [Advanced SIMD and floating-point support](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-21-Advanced-SIMD-and-floating-point-support?lang=en#cihidgdd)
- [Configurable instruction controls](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-22-Configurable-instruction-controls?lang=en#babhdfhd)
