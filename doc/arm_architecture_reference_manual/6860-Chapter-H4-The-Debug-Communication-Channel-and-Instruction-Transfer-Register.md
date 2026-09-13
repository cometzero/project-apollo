# ​Chapter H4 The Debug Communication Channel and Instruction Transfer Register

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H4-The-Debug-Communication-Channel-and-Instruction-Transfer-Register>

### Chapter H4 The Debug Communication Channel and Instruction Transfer Register

This chapter describes communication between a debugger and the implemented debug logic, using the *Debug Communications Channel* (DCC) and the *Instruction Transfer Register* (ITR), and associated control flags. It contains the following sections:

- [Introduction](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H4-The-Debug-Communication-Channel-and-Instruction-Transfer-Register/-H4-1-Introduction?lang=en#babfhfge)
- [DCC and ITR registers](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H4-The-Debug-Communication-Channel-and-Instruction-Transfer-Register/-H4-2-DCC-and-ITR-registers?lang=en#babbaefj)
- [DCC and ITR access modes](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H4-The-Debug-Communication-Channel-and-Instruction-Transfer-Register/-H4-3-DCC-and-ITR-access-modes?lang=en#babbccaf)
- [Flow control of the DCC and ITR registers](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H4-The-Debug-Communication-Channel-and-Instruction-Transfer-Register/-H4-4-Flow-control-of-the-DCC-and-ITR-registers?lang=en#babhfabi)
- [Synchronization of DCC and ITR accesses](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H4-The-Debug-Communication-Channel-and-Instruction-Transfer-Register/-H4-5-Synchronization-of-DCC-and-ITR-accesses?lang=en#babhecbj)
- [Interrupt-driven use of the DCC](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H4-The-Debug-Communication-Channel-and-Instruction-Transfer-Register/-H4-6-Interrupt-driven-use-of-the-DCC?lang=en#babcafeb)
- [Pseudocode description of the operation of the DCC and ITR registers](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H4-The-Debug-Communication-Channel-and-Instruction-Transfer-Register/-H4-7-Pseudocode-description-of-the-operation-of-the-DCC-and-ITR-registers?lang=en#babbjdfd)

> #### Note
>
> Where necessary, [Table K14-1](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-1-Register-name-disambiguation-by-Execution-state?lang=en#tbl_cacgdieg) disambiguates the general register references used in this chapter.
