# Glossary

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary>

### Glossary

A32 instruction
:   A word that specifies an operation to be performed by a PE that is executing in an Exception level that is using AArch32 and is in A32 state. A32 instructions must be word-aligned.

    A32 instructions were previously called ARM instructions.

    See also [A32 state](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaceeaf), [A64 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaehged), [T32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafdiag).

A32 state
:   The AArch32 Instruction set state in which the PE executes A32 instructions.

    A32 state was previously called ARM state.

    See also [T32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafdiag), [T32 state](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadecaf).

A64 instruction
:   A word that specifies an operation to be performed by a PE that is executing in an Exception level that is using AArch64. A64 instructions must be word-aligned. See also [A32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahcjih), [T32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafdiag).

AArch32
:   The 32-bit Execution state. In AArch32 state, addresses are held in 32-bit registers, and instructions in the base instruction sets use 32-bit registers for their processing. AArch32 state supports the T32 and A32 instruction sets.

    See also [AArch64](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadhbic), [A32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahcjih), [T32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafdiag).

AArch64
:   The 64-bit Execution state. In AArch64 state, addresses are held in 64-bit registers, and instructions in the base instruction set can use 64-bit registers for their processing. AArch64 state supports the A64 instruction set.

    See also [AArch32](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahegei), [A64 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaehged).

Abort
:   An exception caused by an illegal memory access. Aborts can be caused by the external memory system or the MMU.

Active element
:   An Active element is an SVE vector element or predicate element that is a source register element or destination register element used by an SVE instruction. When the corresponding element in the instruction’s Governing predicate is TRUE, the element is Active. If an instruction is unpredicated, all of the vector elements or predicate elements are implicitly Active.

Addressing mode
:   Means a method for generating the memory address used by a load/store instruction.

Advanced SIMD
:   A feature of the Arm architecture that provides SIMD operations on a register file of SIMD and floating-point registers. Where an implementation supports both Advanced SIMD and floating-point instructions, these instructions operate on the same register file.

Aligned
:   A data item stored at an address that is exactly divisible by the highest power of 2 that divides exactly into its size in bytes. Aligned halfwords, words and doublewords therefore have addresses that are divisible by 2, 4 and 8 respectively.

    An aligned access is one where the address of the access is aligned to the size of each element of the access.

ALTSP
:   Alternative PARTID space for MPAM.

AMBA
:   Advanced Microcontroller Bus Architecture. The AMBA family of protocol specifications is the Arm open standard for on-chip buses. AMBA provides solutions for the interconnection and management of the functional blocks that make up a *System-on-Chip* (SoC). Applications include the development of embedded systems with one or more processors or signal processors and multiple peripherals.

Analysis of the trace element stream
:   Refers to the process of:

    - Tracing elements that carry information that a trace analyzer requires to enable it to analyze the trace successfully.
    - Tracing elements that either directly indicate program execution, or carry information about program execution.

    A trace element stream might also contain trace elements that contain timing information. This term is distinct from analysis of program execution.

Architecturally executed
:   An instruction is architecturally executed only if it would be executed in a simple sequential execution of the program. When such an instruction has been executed and retired, it has been *architecturally executed*. Any instruction that, in a simple sequential execution of a program, is treated as a `NOP` because it fails its condition code check, is an architecturally executed instruction.

    In a PE that performs speculative execution, an instruction is not architecturally executed if the PE discards the results of a speculative execution.

    See also [Condition code check](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babidaeb), [Simple sequential execution](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfdijc).

Architecturally mapped
:   Where this manual describes a register as being *architecturally mapped* to another register, this indicates that, in an implementation that supports both of the registers, the two registers access the same state.

Architecturally resolved
:   The architectural state (S) associated with an operation (O) is architecturally resolved when S is determined to be identical to the architectural state of O that is visible to the programmer through the execution of the program.

Architecturally UNKNOWN
:   An architecturally UNKNOWN value is a value that is not defined by the architecture but must meet the requirements of the definition of [UNKNOWN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfcabf). Implementations can define the value of the field, but are not required to do so.

    See also [IMPLEMENTATION DEFINED](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babchejb).

Architecturally Allowed Execution
:   An *Architecturally Allowed Execution* must satisfy the [External visibility requirement](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-3-Ordering-requirements-defined-by-the-formal-concurrency-model/-B2-3-9-Definition-of-an-Architecturally-Allowed-Execution?lang=en#chdbcfgj).

ARM core registers
:   Some older documentation uses *ARM core registers* to refer to the following set of registers for execution in AArch32 state:

    - The 13 general-purpose registers, R0-R12, that software can use for processing.
    - SP, the *stack pointer*, that can also be referred to as R13.
    - LR, the *link register*, that can also be referred to as R14.
    - PC, the *Program Counter*, that can also be referred to as R15.

    See also [General-purpose registers](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaiccbf).

ARM instruction
:   See [A32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahcjih).

Associativity
:   See [Cache associativity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjffhc).

Asynchronous accumulation
:   Faults that are accumulated in a status register, where the update to the register is asynchronous to the instruction that causes the fault.

Atomicity
:   Describes either single-copy atomicity or multi-copy atomicity. [Atomicity in the Arm architecture](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-2-Atomicity-in-the-Arm-architecture?lang=en#chdhfcde) defines these forms of atomicity for the Arm architecture.

    See also [Multi-copy atomicity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcicag) and [Single-copy atomicity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babifcje).

    Might also refer to poison-atomicity. See [Poison atomicity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#glossdef_poison_atomicity).

Availability
:   Readiness for correct service.

Banked register
:   A register that has multiple instances, with the instance that is in use depending on the PE mode, Security state, or other PE state.

Baseboard Management Controller
:   A PE dedicated to system control and monitoring.

Base register
:   A register specified by a load/store instruction that is used as the base value for the address calculation for the instruction. Depending on the instruction and its addressing mode, an offset can be added to or subtracted from the base register value to form the virtual address that is sent to memory.

Base register writeback
:   Describes writing back a modified value to the base register used in an address calculation.

Behaves as if
:   Where this manual indicates that a PE *behaves as if* a certain condition applies, all descriptions of the operation of the PE must be re-evaluated taking account of that condition, together with any other conditions that affect operation.

Big-endian memory
:   Means that, for example:

    - A byte or halfword at a word-aligned address is the most significant byte or halfword in the word at that address.
    - A byte at a halfword-aligned address is the most significant byte in the halfword at that address.

    See also [Endianness](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbabhifg), [Little-endian memory](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfeigb).

Blocking
:   Describes an operation that does not permit following instructions to be executed before the operation completes.

    A non-blocking operation can permit following instructions to be executed before the operation completes, and in the event of encountering an exception does not signal an exception to the PE. This enables implementations to retire following instructions while the non-blocking operation is executing, without the need to retain precise PE state.

Branch History Buffer (BHB)
:   The Branch History Buffer is an internal structure that stores branch instruction information including the history of previously executed branches.

Branch prediction
:   Is where a PE selects a future execution path to fetch along. For example, after a branch instruction, the PE can choose to speculatively fetch either the instruction following the branch or the instruction at the branch target.

    See also [Prefetching](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjaibg).

Breakpoint
:   A debug event triggered by the execution of a particular instruction, specified by one or both of the address of the instruction and the state of the PE when the instruction is executed.

Built-in self test (BIST)
:   A mechanism that permits a machine to test itself.

Burst
:   A group of transfers that form a single transaction.

BWA
:   BandWidth Allocation.

BWPBM
:   BandWidth Portion Bit Map.

Byte
:   An 8-bit data item.

CE
:   See [Corrected Error](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#glossdef_corrected_error).

Cache associativity
:   The number of locations in a cache set to which an address can be assigned. Each location is identified by its *way* value.

Cache level
:   The position of a cache in the cache hierarchy. In the Arm architecture, the lower numbered levels are those closest to the PE. For more information, see [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

Cache line
:   The basic unit of storage in a cache. Its size in words is always a power of two, usually 4 or 8 words. A cache line must be aligned to a suitable memory boundary. A *memory cache line* is a block of memory locations with the same size and alignment as a cache line. Memory cache lines are sometimes loosely called cache lines.

Cache lockdown
:   Enables critical software and data to be loaded into the cache so that the cache lines containing them are not subsequently reallocated. It alleviates the delays caused by accessing a cache in a worst-case situation. This ensures that all subsequent accesses to the software and data concerned are cache hits and so complete quickly.

Cache miss
:   A memory access that cannot be processed at high speed because the data it addresses is not in the cache.

Cache sets
:   Areas of a cache, divided up to simplify and speed up the process of determining whether a cache hit occurs. The number of cache sets is always a power of two.

Cache way
:   A cache way consists of one cache line from each cache set. The cache ways are indexed from 0 to (Associativity-1). Each cache line in a cache way is chosen to have the same index as the cache way. For example, cache way *n* consists of the cache line with index *n* from each cache set.

Coherence order
:   See [Coherent](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfggfb).

Coherent
:   Data accesses from a set of observers to a byte in memory are coherent if accesses to that byte in memory by the members of that set of observers are consistent with there being a single total order of all writes to that byte in memory by all members of the set of observers. This single total order of all to writes to that memory location is the *coherence order* for that byte in memory.

Commit window
:   The Commit window defines the range of *P0 elements* that are committed by a *Commit element*. The oldest *P0 element* in the Commit window is the first *P0 element* committed when a *Commit element* occurs. By default, the Commit window starts on the oldest uncommitted *P0 element* and moves forward to the next uncommitted *P0 element*, with each *P0 element* committed by a *Commit element*. The Commit Window Move element moves the start of the Commit window by a number of *P0 elements*, to allow a *Commit element* to commit *P0 elements* that are younger than the oldest uncommitted *P0 elements*, leaving these older *P0 elements* uncommitted.

Completer
:   An agent in a computing system that responds to and completes a memory transaction that was initiated by a Requester.

    See also [Requester](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcdged).

Constructive instruction encoding
:   A constructive instruction encoding is an instruction encoding where the destination register is encoded independently of the source registers.

Condition code check
:   The process of determining whether a conditional instruction executes normally or is treated as a `NOP`. For an instruction that includes a condition code field, that field is compared with the condition flags to determine whether the instruction is executed normally. For a T32 instruction in an IT block, the value of [PSTATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-5-Process-state--PSTATE?lang=en#pstate).IT determines whether the instruction is executed normally.

    See also [Condition code field](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadddci), [Condition flags](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaggfii), [Conditional execution](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahicfa).

Condition code field
:   A 4-bit field in an instruction that specifies the condition under which the instruction executes.

    See also [Condition code check](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babidaeb).

Condition flags
:   The N, Z, C, and V bits of PSTATE, an SPSR, or FPSCR. See the register descriptions for more information.

    See also [Condition code check](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babidaeb), [PSTATE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaijbef).

Conditional execution
:   When a conditional instruction starts executing, if the condition code check returns TRUE, the instruction executes normally. Otherwise, it is treated as a `NOP`.

    See also [Condition code check](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babidaeb).

CONSTRAINED UNPREDICTABLE
:   Where an instruction can result in UNPREDICTABLE behavior, the Armv8 and later architectures specify a narrow range of permitted behaviors. This range is the range of CONSTRAINED UNPREDICTABLE behavior. All implementations that are compliant with the architecture must follow the CONSTRAINED UNPREDICTABLE behavior.

    Execution at Non-secure EL1 or EL0 of an instruction that is CONSTRAINED UNPREDICTABLE can be implemented as generating a trap exception that is taken to EL2, provided that at least one instruction that is not UNPREDICTABLE and is not CONSTRAINED UNPREDICTABLE causes a trap exception that is taken to EL2.

    In body text, the term CONSTRAINED UNPREDICTABLE is shown in SMALL CAPITALS.

    See also [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Containable error
:   See [Contained error](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdhaaahh5).

Contained error
:   An error that is not uncontained or uncontainable.

Context switch
:   The saving and restoring of computational state when switching between different threads or processes. In this manual, the term context switch describes any situation where the context is switched by an operating system and might or might not include changes to the address space.

Context Synchronization event
:   One of:

    - Performing an ISB operation. An ISB operation is performed when an `ISB` instruction is executed and does not fail its condition code check.
    - Exception entry, if any of the following is true:

      - [FEAT\_ExS](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-6-The-Armv8-5-architecture-extension?lang=en#feat_feat_exs) is not implemented.
      - [FEAT\_ExS](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-6-The-Armv8-5-architecture-extension?lang=en#feat_feat_exs) is implemented and the appropriate SCTLR\_ELx.EIS bit is set.
      - The exception is taken to AArch32.
    - Return from an exception, if any of the following is true:

      - [FEAT\_ExS](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-6-The-Armv8-5-architecture-extension?lang=en#feat_feat_exs) is not implemented.
      - [FEAT\_ExS](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-6-The-Armv8-5-architecture-extension?lang=en#feat_feat_exs) is implemented and the appropriate SCTLR\_ELx.EIS bit is set.
      - The exception is returning to AArch32.
      - Exit from Debug state.
    - Executing a `DCPS` instruction.
    - Executing a `DRPS` instruction.

    The effects of a Context synchronization event are:

    - All unmasked interrupts that are pending at the time of the Context synchronization event are taken before the first instruction after the Context synchronization event.
    - If halting is allowed, all Halting debug events that are pending at the time of the Context synchronization event are taken before the first instruction after the Context synchronization event.
    - No instructions appearing in program order after an instruction that causes a Context synchronization event will have performed any part of their functionality until the Context synchronization event has occurred.
    - All direct and indirect writes to System registers that are made before the Context synchronization event affect any instruction, including a direct read, that appears in program order after the instruction causing the Context synchronization event.
    - All completed changes to the translation tables for entries that, before the change, were not permitted to be cached in a TLB, affect all instruction fetches that appear in program order after the instruction causing the Context synchronization event.
    - The following invalidations, if completed before the Context synchronization event will affect all instructions that appear in program order after the Context synchronization event:

      - TLBs.
      - Instruction caches.
      - In AArch32 state branch predictors.
    - In AArch32 state, all Non-cacheable writes that are completed before the Context synchronization event affect all instructions that appear in program order after an instruction causing a Context synchronization event.
    - Changes to the Debug external authentication interfaces that are made before the Context synchronization event affect any instruction that appears in program order after the instruction causing the Context synchronization event.
    - The effect of the completion of any of the instructions added by [FEAT\_SPECRES](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A2-A-profile-Architecture-Extensions/-A2-2-Armv8-A-architecture-extensions/-A2-2-6-The-Armv8-5-architecture-extension?lang=en#feat_feat_specres) is synchronized to the current execution context.
    - Restrictions on the effects of speculation (as described in [Restrictions on the effects of speculation](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-5-Restrictions-on-the-effects-of-speculation?lang=en#chdhjgda)) are observed.
    - Ensuring that the `TSB` instruction is executed in the necessary order with respect to other instructions.
    - Profiling operations for all instructions that are executed in program order are synchronized by execution of a `PSB` instruction before the Context synchronization event.
    - See also:

      - [Restrictions on the effects of speculation](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-5-Restrictions-on-the-effects-of-speculation?lang=en#chdhjgda).
      - [Trace Synchronization Barrier](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-6-Memory-barriers/-B2-6-8-Trace-Synchronization-Barrier?lang=en#beijjegj).
      - [Synchronization and debug exceptions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-12-Synchronization-and-debug-exceptions?lang=en#bcgebfeb).
      - [Synchronization in self-hosted trace](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D3-AArch64-Self-hosted-Trace/-D3-4-Synchronization-in-self-hosted-trace?lang=en#babehbgd).
      - [Synchronization of register updates](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D4-The-Embedded-Trace-Extension/-D4-2-Programmers--model/-D4-2-2-Synchronization-of-register-updates?lang=en#cacccafbh8).
      - [Speculation in the trace element stream](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D4-The-Embedded-Trace-Extension/-D4-3-Trace-elements/-D4-3-3-Speculation-in-the-trace-element-stream?lang=en#chdjdciba9).
      - [Trace Synchronization event](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D6-The-Trace-Buffer-Extension/-D6-6-Synchronization-and-the-Trace-Buffer-Unit/-D6-6-1-Trace-Synchronization-event?lang=en#mdsec_trace_synch_event).
      - [Self-hosted trace extension synchronization rules](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D6-The-Trace-Buffer-Extension/-D6-6-Synchronization-and-the-Trace-Buffer-Unit/-D6-6-3-Self-hosted-trace-extension-synchronization-rules?lang=en#mdsec_armv8p4_synchronization_rules).
      - [Execution, data prediction and prefetching restriction System instructions](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-5-Restrictions-on-the-effects-of-speculation/-B2-5-7-Execution--data-prediction-and-prefetching-restriction-System-instructions?lang=en#chdfeifg).
      - [Synchronization and Statistical Profiling](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D17-The-Statistical-Profiling-Extension/-D17-9-Synchronization-and-Statistical-Profiling?lang=en#chdedead).
      - [Synchronization and Halting debug events](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H3-Halting-Debug-Events/-H3-9-Synchronization-and-Halting-debug-events?lang=en#babgeeca).
      - [Synchronization of memory-mapped registers](/documentation/ddi0487/mc/-Part-I-Memory-mapped-Components-of-the-Arm-Architecture/-Chapter-I1-Requirements-for-Memory-mapped-Components/-I1-2-Synchronization-of-memory-mapped-registers?lang=en#chdhgbbd).
      - [CONSTRAINED UNPREDICTABLE behavior due to inadequate context synchronization](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K1-Architectural-Constraints-on-UNPREDICTABLE-Behaviors/-K1-2-AArch64-CONSTRAINED-UNPREDICTABLE-behaviors/-K1-2-4-CONSTRAINED-UNPREDICTABLE-behavior-due-to-inadequate-context-synchronization?lang=en#cegjdfbf).

    > #### Note
    >
    > - The architecture requires that instructions that generate Context synchronization events do not appear to be executed speculatively, except that the performance monitor counters are permitted to reveal such speculation.
    > - *Context synchronization events* were previously described as *context synchronization operations*.

Conventional memory
:   Memory locations from which generic OSs and application runtimes expect to create allocations for general software use.

Core
:   See [Processing element (PE)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcidja).

CoreSight Address Translation Unit
:   A form of System MMU for trace streams.

Corrected error
:   An error that is detected by hardware and that hardware has corrected.

Counter resolution
:   See [Counter resolution](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D12-The-Generic-Timer-in-AArch64-state/-D12-1-About-the-Generic-Timer/-D12-1-2-The-system-counter?lang=en#counter_resolution_aarch64).

CPBM
:   Cache-Portion Bit Map.

CSU
:   Cache-Storage Usage.

Data independent timing (DIT)
:   The time that it takes to execute a piece of code where the time is not a function of the data being operated on. For more information, see [About PSTATE.DIT](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-5-Software-control-features-and-EL0/-B1-5-6-About-PSTATE-DIT?lang=en#beiccddab3) and [About the DIT bit](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E1-The-AArch32-Application-Level-Programmers--Model/-E1-2-The-Application-level-programmers--model-in-AArch32-state/-E1-2-5-About-the-DIT-bit?lang=en#beiidceg).

Debugger
:   In most of this manual, *debugger* refers to any agent that is performing debug. However, some chapters or parts of this manual require a more rigorous definition, and define debugger locally. See:

    - [Definition of a debugger in the context of self-hosted debug](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D2-AArch64-Self-hosted-Debug/-D2-1-About-self-hosted-debug/-D2-1-1-Definition-of-a-debugger-in-the-context-of-self-hosted-debug?lang=en#cegdhieg).
    - [Definition of a debugger in the context of self-hosted debug](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G2-AArch32-Self-hosted-Debug/-G2-1-About-self-hosted-debug/-G2-1-1-Definition-of-a-debugger-in-the-context-of-self-hosted-debug?lang=en#cegdihed).
    - [Definition and constraints of a debugger in the context of external debug](/documentation/ddi0487/mc/-Part-H-External-Debug/-Chapter-H1-About-External-Debug/-H1-1-Introduction-to-external-debug/-H1-1-1-Definition-and-constraints-of-a-debugger-in-the-context-of-external-debug?lang=en#chdchaag).

Deferred error
:   An error that has not been silently propagated but does not require immediate action at the producer. The error might have passed from the producer to a consumer.

Deprecated
:   Something that is present in the Arm architecture for backward compatibility.

    Features that are deprecated but are not OPTIONAL are present in current implementations of the Arm architecture, but might not be present, or might be deprecated and OPTIONAL, in future versions of the Arm architecture.

    Arm strongly recommends software to avoid using deprecated features. Where a feature is deprecated for performance reasons, Arm strongly recommends software to avoid using that feature because of the likelihood of the significant negative impact on performance.

    See also [OPTIONAL](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#glossdef_optional).

Destructive instruction encoding
:   A destructive instruction encoding is an instruction encoding where one of the source registers is also used as the destination register.

Detected error
:   An error that has been detected and signaled to a consumer.

Detected Uncorrected error
:   A detected error that has not been be corrected and causes failure.

Digital signal processing (DSP)
:   Algorithms for processing signals that have been sampled and converted to digital form. DSP algorithms often use saturated arithmetic.

Direct branch
:   Branch instructions whose target is relative to the PC of the branch and the offset is determined solely from the opcode of the executed instruction.

    See also [Indirect branch](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#indirect_branch).

Direct Memory Access (DMA)
:   An operation that accesses main memory directly, without the PE performing any accesses to the data concerned.

Direct read
:   A direct read of a System register is a read performed by a System register access instruction in which the contents of the System Register addressed by {`op1`, `Crm`, `Crn`, `op2`}

    For more information, see [Direct read](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-1-About-the-AArch64-System-registers/-D24-1-2-General-behavior-of-accesses-to-the-AArch64-System-registers?lang=en#babgjcgg).

    See also [Direct write](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhjacgc), [Indirect read](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhgghgb), [Indirect write](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhdidjb).

Direct write
:   A direct write of a System register is a write performed by a System register access instruction.

    For more information, see [Direct write](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-1-About-the-AArch64-System-registers/-D24-1-2-General-behavior-of-accesses-to-the-AArch64-System-registers?lang=en#babbgafa).

    See also [Direct read](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhfiidi), [Indirect read](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhgghgb), [Indirect write](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhdidjb).

DMA
:   See [Direct Memory Access (DMA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babeabhj).

DNM
:   See [Do-Not-Modify (DNM)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babeaabd).

Domain
:   In the Arm architecture, *domain* is used in the following contexts.

    Shareability domain
    :   Defines a set of observers for which the Shareability attributes make the data or unified caches transparent for data accesses.

    Power domain
    :   Defines a block of logic with a single, common, power supply.

    Memory regions domain
    :   When using the Short-descriptor translation table format, defines a collection of Sections, Large pages and Small pages of memory, that can have their access permissions switched rapidly by writing to the *Domain Access Control Register* (DACR). Arm deprecates any use of memory regions domains.

Do-Not-Modify (DNM)
:   Means the value must not be altered by software. DNM fields read as UNKNOWN values, and must only be written with the value read from the same field on the same PE.

Double-precision value
:   Consists of two consecutive 32-bit words that are interpreted as a basic double-precision floating-point number according to the *IEEE Standard for Floating-point Arithmetic*.

Doubleword
:   A 64-bit data item. Doublewords are normally at least word-aligned in Arm systems.

Doubleword-aligned
:   Means that the address is divisible by 8.

Downstream
:   The direction from Requesters to Completers.

DSB
:   Data Synchronization Barrier.

DSP
:   See [Digital signal processing (DSP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcfhbf).

DUE
:   See [Detected Uncorrected error](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#glossdef_detected_uncorrected_error).

DUE FIT RATE
:   The FIT rate for failures from a DUE.

ECC
:   See [Error Correction Code (ECC)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdhheiee7).

EDAC
:   See [Error Correction Code (ECC)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdhheiee7).

EDC
:   See [Error Detection Code (EDC)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdiicdhh8).

Effective frequency
:   See [Effective frequency](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D12-The-Generic-Timer-in-AArch64-state/-D12-1-About-the-Generic-Timer/-D12-1-2-The-system-counter?lang=en#effective_frequency_aarch64).

Effective value
:   A register control field, meaning a field in a register that controls some aspect of the behavior, can be described as having an *Effective value*:

    - In some cases, the description of a control *a* specifies that when control *a* is active it causes a register control field *b* to be treated as having a fixed value for all purposes other than direct reads, or direct reads and direct writes, of the register containing control field *b*. When control *a* is active that fixed value is described as the *Effective value* of register control field *b*. For example, when the value of [HCR](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G8-AArch32-System-Register-Descriptions/-G8-2-General-system-control-registers/-G8-2-65-HCR--Hyp-Configuration-Register?lang=en#reg_aarch32_hcr).DC is 1, the *Effective value* of [HCR](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G8-AArch32-System-Register-Descriptions/-G8-2-General-system-control-registers/-G8-2-65-HCR--Hyp-Configuration-Register?lang=en#reg_aarch32_hcr).VM is 1, regardless of its actual value.

      In other cases, in some contexts a register control field *b* is not implemented or is not accessible, but behavior of the PE is as if control field *b* was implemented and accessible, and had a particular value. In this case, that value is the *Effective value* of register control field *b*.

      > #### Note
      >
      > Where a register control field is introduced in a particular version of the architecture, and is not implemented in an earlier version of the architecture, typically it will have an *Effective value* in that earlier version of the architecture.
    - Otherwise, the *Effective value* of a register control field is the value of that field.

Effective Non-streaming SVE vector length
:   The Non-streaming SVE vector length in bits at the current Exception level, is an implementation-supported power of two up to the Maximum implemented Non-streaming SVE vector length, further constrained by ZCR\_ELx at the current and higher Exception levels.

    See also [Configurable SVE vector lengths](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-2-Configurable-SVE-vector-lengths?lang=en#beijgdghi3).

Effective Streaming SVE vector length
:   The Streaming SVE vector length in bits at the current Exception level is an implementation-supported power of two from 128 up to the Maximum implemented Streaming SVE vector length, further constrained by SMCR\_ELx at the current and higher Exception levels.

    See also [Configurable SVE vector lengths](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-2-Configurable-SVE-vector-lengths?lang=en#beijgdghi3).

Effective SVE vector length
:   The vector length in bits that applies to the execution of SVE instructions at the current Exception level is the Effective Streaming SVE vector length when the PE is in Streaming SVE mode, otherwise it is the Effective Non-streaming SVE vector length.

    See also [Configurable SVE vector lengths](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-2-Configurable-SVE-vector-lengths?lang=en#beijgdghi3).

Element number
:   For a given element size of N bits, elements within a vector or predicate register are numbered with element[0] always representing bits[(N-1):0], element[1] always representing bits[(2N-1):N], and so on.

Endianness
:   An aspect of the system memory mapping.

    See also [Big-endian memory](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbcjai) and [Little-endian memory](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfeigb).

Error Correction Code (ECC)
:   A code capable of detecting and correcting a number of errors.

Error Detection Code (EDC)
:   A code capable of detecting, but not correcting, errors.

Error propagation
:   Passing an error from a producer to a consumer.

Error record
:   Data recorded about an error, usually by hardware.

ETEEvent
:   A feature of the trace unit that is used to generate *Event elements* and drive External Outputs. Each ETEEvent can be programmed to be sensitive to resource events.

Event trace
:   The trace uses *Event elements* that indicate certain events have occurred in the program that the PE is executing. The program events to be indicated are selected before a trace session.

Exceptional occurrence
:   Events indicated by an *Exception element* by the ETE architecture, including the following:

    - PE architectural exceptions.
    - ETE defined exceptions.
    - IMPLEMENTATION DEFINED exceptions.

Exception
:   Handles an event. For example, an exception could handle an external interrupt or an undefined instruction.

Exception vector
:   A fixed address that contains the address of the first instruction of the corresponding exception handler.

Executing processing element (PEe)
:   The name given to an example PE that executes a specified instruction.

    See also [Processing element (PE)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcidja).

Execution stream
:   The stream of instructions that would have been executed by sequential execution of the program.

External abort
:   An abort that is generated by the external memory system.

Fault
:   An event that causes the program to deviate from the intended behavior, for example an invalid translation.

Field Replaceable Unit (FRU)
:   A component or unit in a system that can be replaced without return to base.

First active element
:   The First active element of an SVE vector or predicate register is the lowest numbered element that is an Active element.

First-fault load
:   SVE provides a First-fault option for some SVE vector load instructions. This option causes memory access faults to be suppressed if they do not occur as a result of the First active element of the vector. Instead, the FFR is updated to indicate which of the Active elements were not successfully loaded.

Flat address mapping
:   Is where the physical address for every access is equal to its virtual address.

Flush-to-zero mode
:   A processing mode that optimizes the performance of some floating-point algorithms by replacing the denormalized operands and Intermediate results with zeros, without significantly affecting the accuracy of their final results.

FRU
:   See [Field Replaceable Unit (FRU)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdbfbefd1).

Gather-load
:   Gather-load is a mechanism that allows the elements of a vector to be read from non-contiguous memory locations using a vector of addresses, where the addresses are constructed according to the addressing mode.

General-purpose registers ​
:   The registers that the base instructions use for processing:

    - In AArch64 state the general-purpose registers are:

      - W0-W30 when accessed as 32-bit registers.
      - X0-X30 when accessed as 64-bit registers.
    - In AArch32 state the general-purpose registers are R0-R14, that can also be described as R0-R12, SP, LR.

      > #### Note
      >
      > Older documentation defines the AArch32 general-purpose registers as R0-R12, and the Arm core registers as R0-R12, SP, LR, and PC.

See also [High registers](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbhhbb), [Low registers](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babhegdh).

Generic Interrupt Controller (GIC)
:   Arm system architecture interrupt controller for IRQ and FIQ interrupt exceptions.

Governing predicate
:   The predicate register that is used to determine the Active elements of a predicated instruction is known as the Governing predicate for that instruction.

GIC
:   See [Generic Interrupt Controller (GIC)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdhccbbc8).

GPC
:   See [Granule Protection Check](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdicbjfa1).

Granule Protection Check
:   A mechanism for checking the protection information of a particular physical address and physical address space, For more information, see [The Granule Protection Check Mechanism](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D9-The-Granule-Protection-Check-Mechanism?lang=en#babdhdbgc2).

Halfword
:   A 16-bit data item. Halfwords are normally halfword-aligned in Arm systems.

Halfword-aligned
:   Means that the address is divisible by 2.

High registers ​
:   In AArch32 state, the general-purpose registers R8-R14. Most 16-bit T32 instructions cannot access the high registers.

    > #### Note
    >
    > In some contexts, *high registers* refers to R8-R15, meaning R8-R14 and the PC.

    See also [General-purpose registers](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaiccbf), [Low registers](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babhegdh).

High vectors
:   An alternative location for the exception vectors. The high vector address range is near the top of the address space, rather than at the bottom.

ICN
:   InterConnect Network.

IGNORED
:   Indicates that the architecture guarantees that the bit or field is not interpreted or modified by hardware.

    In body text, the term IGNORED is shown in SMALL CAPITALS.

Illegal
:   In the context of SME, describes an implemented instruction whose attempted execution by a PE when `PSTATE.SM` and `PSTATE.ZA` are not in the required state causes an SME illegal instruction exception to be taken, unless its execution at the current Exception level is prevented by a higher priority configurable trap or enable.

    See [Streaming SVE mode](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-6-Streaming-SVE-mode?lang=en#beigieigd1).

Immediate and offset fields
:   Are unsigned unless otherwise stated.

Immediate value
:   A value that is encoded directly in the instruction and used as numeric data when the instruction is executed. Many instructions can be used with an immediate argument.

IMP
:   An abbreviation used in diagrams to indicate that one or more bits have IMPLEMENTATION DEFINED behavior.

IMPLEMENTATION DEFINED
:   Means that the behavior is not architecturally defined, but must be defined and documented by individual implementations.

    In body text, the term IMPLEMENTATION DEFINED is shown in SMALL CAPITALS.

IMPLEMENTATION SPECIFIC
:   Means that the behavior is not architecturally defined, and might not be documented by an individual implementation. Used when there are several implementation options available and the option chosen does not affect software compatibility.

    In body text, the term IMPLEMENTATION SPECIFIC is shown in SMALL CAPITALS.

Imprecise exception
:   An exception that is not precise.

Inactive element
:   An Inactive element is an SVE vector element or predicate element that is an unused source register element or destination register element for the associated instruction. When the corresponding element of an instruction's Governing predicate is FALSE, it is an Inactive element.

Index register
:   A register specified in some load and store instructions. The value of this register is used as an offset to be added to or subtracted from the base register value to form the virtual address that is sent to memory. Some instruction forms permit the index register value to be shifted before the addition or subtraction.

Indirect branch
:   Branch instructions that are not direct branches.

    See also [Direct branch](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#direct_branch).

Indirect read
:   An Indirect System Register Read is a System Register Read which is not a Direct System Register Read Effect. For example, when an instruction uses a System register value to establish operating conditions, that use of the System register is an indirect read of the System register.

    For more information, including additional examples of indirect reads, see [Indirect read](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-1-About-the-AArch64-System-registers/-D24-1-2-General-behavior-of-accesses-to-the-AArch64-System-registers?lang=en#babiaddf).

    See also [Direct read](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhfiidi), [Direct write](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhjacgc), [Indirect write](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhdidjb).

Indirect write
:   An indirect write of a System register occurs when the contents of a register are updated by some mechanism other than a [Direct write](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhjacgc) to that register. For example, an indirect write to a register might occur as a side-effect of executing an instruction that does not perform a direct write to the register, or because of some operation performed by an external agent.

    For more information, see [Indirect write](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D24-AArch64-System-Register-Descriptions/-D24-1-About-the-AArch64-System-registers/-D24-1-2-General-behavior-of-accesses-to-the-AArch64-System-registers?lang=en#babfeahb).

    See also [Direct read](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhfiidi), [Direct write](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhjacgc), [Indirect read](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbhgghgb).

Inline literals
:   These are constant addresses and other data items held in the same area as the software itself. They are automatically generated by compilers, and can also appear in assembler code.

Intermediate physical address (IPA)
:   An implementation of virtualization, the address to which a Guest OS maps a VA. A hypervisor might then map the IPA to a PA. Typically, the Guest OS is unaware of the translation from IPA to PA.

    See also [Physical address (PA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babehcfi), [Virtual address (VA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdadgb).

Interrupt
:   In a PE context, an asynchronous exception. There are three interrupt exceptions: IRQ, FIQ, and SError. IRQ and FIQ are always precise. In a system architecture context, an asynchronous event sent to a PE or GIC for processing as an interrupt exception.

Interworking
:   A method of working that permits branches between software using the T32 and A32 instruction sets.

IPA
:   See [Intermediate physical address (IPA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babgfifb).

kvm
:   Kernel-based Virtual Machine, an open-source software package that implements a type-2 hypervisor within Linux.

Latent error
:   An error that is present in a system but not yet detected.

Last active element
:   The Last active element of an SVE vector or predicate register is the highest numbered element that is an Active element.

Legal
:   Describes an implemented instruction that can be executed by a PE when `PSTATE.SM` and `PSTATE.ZA` are in the required state, unless its execution at the current Exception level is prevented by a configurable trap or enable.

    See [Streaming SVE mode](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-6-Streaming-SVE-mode?lang=en#beigieigd1).

Level
:   See [Cache level](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babffjai).

Level of Coherence (LoC)
:   The last level of cache that must be cleaned or invalidated when cleaning or invalidating to the point of coherency. For more information, see [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

    See also [Cache level](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babffjai), [Point of coherency (PoC)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbfbff).

Level of Unification, Inner Shareable (LoUIS)
:   The last level of cache that must be cleaned or invalidated when cleaning or invalidating to the point of unification for the Inner Shareable Shareability domain. For more information, see [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

    See also [Cache level](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babffjai), [Point of unification (PoU)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcbhb).

Level of Unification, uniprocessor (LoUU)
:   For a PE, the last level of cache that must be cleaned or invalidated when cleaning or invalidating to the point of unification for that PE. For more information, see [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

    See also [Cache level](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babffjai), [Point of unification (PoU)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcbhb).

Line
:   See [Cache line](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcgdgg).

Little-endian memory
:   Means that, for example:

    - A byte or halfword at a word-aligned address is the least significant byte or halfword in the word at that address.
    - A byte at a halfword-aligned address is the least significant byte in the halfword at that address.

    See also [Big-endian memory](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbcjai), [Endianness](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbabhifg).

Load/store architecture
:   An architecture where data-processing operations only operate on register contents, not directly on memory contents.

LoC
:   See [Level of Coherence (LoC)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbaaaa).

LoUIS
:   See [Level of Unification, Inner Shareable (LoUIS)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babhihch).

LoUU
:   See [Level of Unification, uniprocessor (LoUU)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhggd).

Lockdown
:   See [Cache lockdown](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babggbfi).

Low registers ​
:   In AArch32 state, general-purpose registers R0-R7. Unlike the high registers, all T32 instructions can access the Low registers.

    See also [General-purpose registers](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaiccbf), [High registers](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbhhbb).

LPI
:   Locality-specific Peripheral Interrupt.

Maximum implemented Non-streaming SVE vector length
:   The maximum Non-streaming SVE vector length in bits supported by the implementation.

    See [Maximum implemented SVE vector lengths](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-1-Maximum-implemented-SVE-vector-lengths?lang=en#beiceffjj1)

Maximum implemented Streaming SVE vector length
:   The maximum Streaming SVE vector length in bits supported by the implementation.

    See [Maximum implemented SVE vector lengths](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-1-Maximum-implemented-SVE-vector-lengths?lang=en#beiceffjj1)

Maximum implemented SVE vector length
:   The maximum vector length in bits that applies to the execution of SVE instructions at the current Exception level is the Maximum implemented Streaming SVE vector length when the PE is in Streaming SVE mode; otherwise it is the Maximum implemented Non-streaming SVE vector length.

    See [Maximum implemented SVE vector lengths](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-1-Maximum-implemented-SVE-vector-lengths?lang=en#beiceffjj1).

MEC
:   See [Memory Encryption Contexts](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdiebjhd8).

MBWU
:   Memory BandWidth Usage.

Memory barrier
:   See [Memory barriers](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-6-Memory-barriers?lang=en#beigfafg).

Memory coherency
:   The problem of ensuring that when a memory location is read, either by a data read or an instruction fetch, the value actually obtained is always the value that was most recently written to the location. This can be difficult when there are multiple possible physical locations, such as main memory and at least one of a write buffer and one or more levels of cache.

Memory element
:   An item of data in memory that is transferred to or from a vector element by an SVE load or store instruction. Each memory element has an access size and a type. The memory element access size is specified by each load and store instruction independently of the vector element size.

Memory Encryption Contexts
:   Unique cryptographic boundaries provided to the Realm physical address space for assignment to Realm virtual machines, with policy controlled by Realm EL2. For more information, see [Memory Encryption Contexts](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-4-Memory-Encryption-Contexts?lang=en#mdsec_memoryencryptioncontexts).

Memory Management Unit (MMU)
:   Provides detailed control of the part of a memory system that provides a single stage of address translation. Most of the control is provided using translation tables that are held in memory, and define the attributes of different regions of the physical memory map.

Memory Protection Unit (MPU)
:   A hardware unit whose registers provide simple control of a limited number of protection regions in memory.

Merging predication
:   When a predicated SVE instruction specifies merging predication, the Inactive elements of the destination register remain unchanged.

Memory system component
:   MSC. A function, unit, or design block in a memory system that can have partitionable resources. MSCs consist of all units that handle load or store requests issued by any MPAM Requester. These can include cache memories, interconnects, memory management units, memory channel controllers, queues, buffers, and rate adapters. An MSC can contain one or more resources that each can have zero or more resource partitioning controls. For example, a PE can contain several caches, each of which might have zero or more resource partitioning controls.

Memory system resource
:   A resource that affects the performance of software's use of the memory system and is either local to an MSC (such as cache-memory capacity) or non-local (such as memory bandwidth, which is present over an entire path, from Requester to Completer, that can pass through multiple MSCs).

MMR
:   Memory-mapped Register.

MPAM
:   Memory system resource Partitioning and Monitoring.

MPAM information
:   The MPAM information bundle, comprising PARTID, PMG, and MPAM\_NS.

MPAM resource partition
:   See [Resource partition](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#bgbecadcf4).

Microarchitecturally-finished
:   An operation that has finished all of its operational pseudocode, although the results of any memory accesses, including translation table walks and updates, are not yet coherent with other observers.

Microarchitecturally-unfinished
:   An operation that has not completed all of its operational pseudocode.

Miss
:   See [Cache miss](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdejha).

MMU
:   See [Memory Management Unit (MMU)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babggicd).

MPU
:   See [Memory Protection Unit (MPU)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgea).

Multi-copy atomicity
:   The form of atomicity described in [Requirements for multi-copy atomicity](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-2-Atomicity-in-the-Arm-architecture/-B2-2-4-Requirements-for-multi-copy-atomicity?lang=en#chdhhhcb).

    See also [Atomicity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babefgdg), [Single-copy atomicity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babifcje).

NaN
:   Not a Number. A floating-point value that can be used when neither a numeric value nor an infinity is appropriate. A NaN can be a *quiet* NaN, that propagate through most floating-point operations, or a *signaling* NaN, that causes an Invalid Operation floating-point exception when used. For more information, see the *IEEE Standard for Floating-point Arithmetic*.

    See also [Quiet NaN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbabfcaf), [Signaling NaN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafeaih).

Natural eviction
:   A natural eviction is an eviction that occurs in the course of the normal operation of the memory system, rather than because of an operation that explicitly causes an eviction from the cache, such as the execution of a cache maintenance instruction. Typically, a natural eviction occurs when the caching algorithm requires data to be cached but the cache does not have room for that data.

Non-fault load
:   SVE provides a Non-fault option for some SVE vector load instructions. This option causes all memory access faults to be suppressed. Instead, the FFR is updated to indicate which of the Active elements were not successfully loaded.

NSVL
:   See [Effective Non-streaming SVE vector length](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdecfggb4).

Observer
:   An observer is one of:

    - The mechanism inside a PE that generates Implicit Translation Table Descriptor (TTD) Memory Effects.
    - The mechanism inside a PE that generates Implicit Instruction Memory Read Effects.
    - The mechanism inside a PE that generates Explicit Memory Effects, Tag Memory Effects, Barrier Effects, Instruction Fetch Barrier Effects, TLBI Effects, DC Effects, IC Effects, Fault Effects, or GCS Effects.
    - The mechanism inside a PE that generates Memory Effects for SPE.
    - The mechanism inside a PE that generates Memory Effects for TRBE.
    - The mechanism inside a PE that generates Memory Effects for HDBSS.
    - The mechanism inside a PE that generates Memory Effects for HACDBS.
    - Any mechanism outside the PE that can generate Memory Effects, for example, a peripheral device, an SMMU, or a GIC.

Obsolete
:   Obsolete indicates something that is no longer supported by Arm. When an architectural feature is described as obsolete, this indicates that the architecture has no support for that feature, although an earlier version of the architecture did support it.

Offset addressing
:   Means that the memory address is formed by adding or subtracting an offset to or from the base register value.

OPTIONAL
:   When applied to a feature of the architecture, OPTIONAL indicates a feature that is not required in an implementation of the Arm architecture:

    - If a feature is OPTIONAL and deprecated, this indicates that the feature is being phased out of the architecture. Arm expects such a features to be included in a new implementation only if there is a known backward-compatibility reason for the inclusion of the feature.

      A feature that is OPTIONAL and deprecated might not be present in future versions of the architecture.
    - A feature that is OPTIONAL but not deprecated is, typically, a feature added to a version of the Arm architecture after the initial release of that version of the architecture. Arm recommends that such features are included in all new implementations of the architecture.

    In body text, these meanings of the term OPTIONAL are shown in SMALL CAPITALS.

    > #### Note
    >
    > Do not confuse these Arm-specific uses of OPTIONAL with other uses of *optional*, where it has its usual meaning. These include:
    >
    > - Optional arguments in the syntax of many instructions.
    > - Behavior determined by an implementation choice, for example the optional byte order reversal in an Armv7-R implementation, where the [SCTLR](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G8-AArch32-System-Register-Descriptions/-G8-2-General-system-control-registers/-G8-2-127-SCTLR--System-Control-Register?lang=en#reg_aarch32_sctlr).IE bit indicates the implemented option.

    See also [Deprecated](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#glossdef_deprecated).

Other-multi-copy atomic
:   This is a Memory Write effect from an observer that, if observed by a different observer, is then observed by all other observers that access the location coherently.

PA
:   See [Physical address (PA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babehcfi).

Packed access
:   A memory access that is performed as a result of an SVE load or store instruction for which the vector element size and the memory element size are the same.

PCIe
:   See [Peripheral Component Interconnect Express (PCI Express or PCIe)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdjgaigb4).

PE
:   See [Processing element (PE)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcidja).

Peripheral Component Interconnect Express (PCI Express or PCIe)
:   A high-speed serial computer expansion bus standard maintained and developed by the PCI Special Interest Group.

PEe
:   The executing processing element. See [Executing processing element](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#glossdef_executing_pe).

PFA
:   See [Predictive Failure Analysis (PFA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdjedjhj1).

Physical address (PA)
:   An address that identifies a location in the physical memory map.

    See also [Intermediate physical address (IPA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babgfifb), [Virtual address (VA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdadgb).

Point of coherency (PoC)
:   See [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj) for the AArch64 state and [Terminology for Clean, Invalidate, and Clean and Invalidate instructions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G4-The-AArch32-System-Level-Memory-Model/-G4-4-AArch32-cache-and-branch-predictor-support/-G4-4-6-About-cache-maintenance-in-AArch32-state?lang=en#beijgaia) for the AArch32 state.

Point of Deep Persistence (PoDP)
:   See [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

Point of encryption (PoE)
:   See [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

Point of persistence (PoP)
:   See [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

Point of physical aliasing (PoPA)
:   See [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

Point of physical storage (PoPS)
:   See [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj).

Point of unification (PoU)
:   See [Terms used in describing the cache maintenance instructions](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D7-The-AArch64-System-Level-Memory-Model/-D7-5-Cache-support/-D7-5-8-About-cache-maintenance-in-AArch64-state?lang=en#beijjacj) for the AArch64 state and [Terminology for Clean, Invalidate, and Clean and Invalidate instructions](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G4-The-AArch32-System-Level-Memory-Model/-G4-4-AArch32-cache-and-branch-predictor-support/-G4-4-6-About-cache-maintenance-in-AArch32-state?lang=en#beijgaia) for the AArch32 state.

Poison atomicity
:   The form of atomicity described in [Clearing Deferred errors from poisoned Locations](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D20-RAS-PE-Architecture/-D20-2-PE-error-handling/-D20-2-3-Clearing-Deferred-errors-from-poisoned-Locations?lang=en#mdsec_clearing_deferred_errors_from_poisoned_locations).

    See also [Atomicity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babefgdg).

Poison granule
:   A region of naturally-aligned memory affected by poison.

    See [Error propagation](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A1-Introduction-to-the-Arm-Architecture/-A1-7-Reliability--Availability--and-Serviceability/-A1-7-3-General-taxonomy-of-errors?lang=en#mdsec_error_propagation) for information on poison.

Post-indexed addressing
:   Means that the memory address is the base register value, but an offset is added to or subtracted from the base register value and the result is written back to the base register.

Precise exception
:   An exception where the exception handler receives the state of the PE and the state of the memory system consistent with the PE having executed all of the instructions up to, but not including, the point in the instruction stream where the exception was taken. The state of the PE and the state of the memory do not include instructions that occurred after this point.

Predicate
:   A one-dimensional array of predicate elements of the same size.

Predicate element
:   Individual subdivisions of a predicate register that can be 1, 2, 4, or 8 bits in size. The predicate element size is specified independently by each instruction and is always one-eighth the size of the corresponding vector element. The lowest-numbered bit of each predicate element holds the Boolean value of that element, where 1 represents TRUE and 0 represents FALSE.

Predicated instruction
:   An SVE instruction that has a Governing predicate operand, which determines the Active and Inactive elements for that instruction.

Predicate register
:   An SVE predicate register, P0-P15, having a length that is a power of two, in the range 16 bits to 256 bits, inclusive.

Predictive Failure Analysis (PFA)
:   Mechanisms to analyze errors and predict future failures.

Prefetching
:   Prefetching refers to speculatively fetching instructions or data from the memory system. In particular, instruction prefetching is the process of fetching instructions from memory before the instructions that precede them, in simple sequential execution of the program, have finished executing. Prefetching an instruction does not mean that the instruction has to be executed.

    In this manual, references to instruction or data fetching apply also to prefetching, unless the context explicitly indicates otherwise.

    > #### Note
    >
    > The Prefetch Abort exception can be generated on any instruction fetch, and is not limited to speculative instruction fetches.

    See also [Simple sequential execution](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfdijc).

Prefixed instruction
:   The instruction that immediately follows a MOVPRFX instruction in program order.

Pre-indexed addressing
:   Means that the memory address is formed in the same way as for offset addressing, but the memory address is also written back to the base register.

Processing element (PE)
:   The abstract machine defined in the Arm architecture, as documented in an Arm Architecture Reference Manual. A PE implementation compliant with the Arm architecture must conform with the behaviors described in the corresponding Arm Architecture Reference Manual.

Protection granule
:   A quantum of memory for which an EDC or ECC provides detection or correction. For example, a 72/64 SECDED ECC scheme has a 64-bit protection granule.

Protection region
:   A memory region whose position, size, and other properties are defined by Memory Protection Unit registers.

Protection Unit
:   See [Memory Protection Unit (MPU)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgea).

Pseudo-instruction
:   UAL assembler syntax that assembles to an instruction encoding that is expected to disassemble to a different assembler syntax, and is described in this manual under that other syntax. For example, `MOV <Rd>, <Rm>, LSL #<n>` is a pseudo-instruction that is expected to disassemble as `LSL <Rd>, <Rm>, #<n>`.

PSTATE
:   An abstraction of process state information. All of the instruction sets provide instructions that operate on elements of PSTATE.

    See also [Condition flags](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaggfii).

Quadword
:   A 128-bit data item. Quadwords are normally at least word-aligned in Arm systems.

Quadword-aligned
:   Means that the address is divisible by 16.

Quiet NaN
:   A NaN that propagates unchanged through most floating-point operations.

    See also [NaN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbabcdaj), [Signaling NaN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafeaih).

RAO
:   See [Read-As-One (RAO)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babeajdc).

RAZ
:   See [Read-As-Zero (RAZ)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbdfbe).

RAO/SBOP
:   In versions of the Arm architecture before Armv8, Read-As-One, Should-Be-One-or-Preserved on writes.

    From the introduction of the Armv8 architecture, RES1 replaces this description.

    See also [UNK/SBOP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaehjdf), [Read-As-One (RAO)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babeajdc), [RES1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadihjb), [Should-Be-One-or-Preserved (SBOP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babghfch).

RAO/WI
:   Read-As-One, Writes Ignored.

    Hardware must implement the field as Read-As-One, and must ignore writes to the field.

    Software can rely on the field reading as all 1s, and on writes being ignored.

    This description can apply to a single bit that reads as 1, or to a field that reads as all 1s.

    See also [Read-As-One (RAO)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babeajdc).

RAZ/SBZP
:   In versions of the Arm architecture before Armv8, Read-As-Zero, Should-Be-Zero-or-Preserved on writes.

    From the introduction of the Armv8 architecture, RES0 replaces this description.

    See also [UNK/SBZP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaehhhh), [Read-As-Zero (RAZ)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbdfbe), [RES0](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahedde), [Should-Be-Zero-or-Preserved (SBZP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babiiibg).

RAZ/WI
:   Read-As-Zero, Writes Ignored.

    Hardware must implement the field as Read-As-Zero, and must ignore writes to the field.

    Software can rely on the field reading as all 0s, and on writes being ignored.

    This description can apply to a single bit that reads as 0, or to a field that reads as all 0s.

    See also [Read-As-Zero (RAZ)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbdfbe).

Read-allocate cache
:   A cache in which a cache miss on reading data causes a cache line to be allocated into the cache.

Read-As-One (RAO)
:   Hardware must implement the field as reading as all 1s.

    Software:

    - Can rely on the field reading as all 1s.
    - Must use a [SBOP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadjhga) policy to write to the field.

    This description can apply to a single bit that reads as 1, or to a field that reads as all 1s.

    See also [RAO/SBOP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahcfbc), [RAO/WI](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahcdee), [RES1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadihjb).

Read-As-Zero (RAZ)
:   Hardware must implement the field as reading as all 0s.

    Software:

    - Can rely on the field reading as all 0s
    - Must use a [SBZP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadiida) policy to write to the field.

    This description can apply to a single bit that reads as 0, or to a field that reads as all 0s.

    See also [RAZ/SBZP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaiiehc), [RAZ/WI](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbagjhaj), [RES0](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahedde).

Read-to-Clear (RC)
:   A read of the field clears the field to 0 once the read is complete.

Read, modify, write
:   In a read, modify, write instruction sequence, a value is read to a general-purpose register, the relevant fields updated in that register, and the new value written back.

Recoverable error
:   A contained error that must be corrected to allow the correct operation of the system or smaller parts of the system to continue.

Reliability
:   Continuity of correct service.

Requester
:   An agent in a computing system that is capable of initiating memory transactions.

    See also [Completer](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcgbfg).

RES0
:   A reserved bit. Used for fields in register descriptions, and for fields in architecturally-defined data structures that are held in memory, for example in translation table descriptors.

    Within the architecture, there are some cases where a register bit or field:

    - Is RES0 in some defined architectural context.
    - Has different defined behavior in a different architectural context.

    > #### Note
    >
    > - RES0 is not used in descriptions of instruction encodings.
    > - Where an AArch32 System register is [Architecturally mapped](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadchjc) to an AArch64 System register, and a bit or field in that register is RES0 in one Execution state and has defined behavior in the other Execution state, this is an example of a bit or field with behavior that depends on the architectural context.

    This means the definition of RES0 for fields in read/write registers is:

    If a bit is RES0 in all contexts
    :   For a bit in a read/write register, it is IMPLEMENTATION DEFINED whether:

        1. The bit is hardwired to 0. In this case:

           - Reads of the bit always return 0.
           - Writes to the bit are ignored.
        2. The bit can be written. In this case:

           - An indirect write to the register sets the bit to 0.
           - A read of the bit returns the last value successfully written, by either a direct or an indirect write, to the bit.

             If the bit has not been successfully written since reset, then the read of the bit returns the reset value if there is one, or otherwise returns an UNKNOWN value.
           - A direct write to the bit must update a storage location associated with the bit.
           - The value of the bit must have no effect on the operation of the PE, other than determining the value read back from the bit, unless this Manual explicitly defines additional properties for the bit.

        Whether RES0 bits or fields follow behavior [1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbacfbhj) or behavior [2](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbajcbii) is IMPLEMENTATION DEFINED on a bit-by-bit basis.

    If a bit is RES0 only in some contexts
    :   For a bit in a read/write register, when the bit is described as RES0:

        - An indirect write to the register sets the bit to 0.
        - A read of the bit must return the value last successfully written to the bit, by either a direct or an indirect write, regardless of the use of the register when the bit was written.

          If the bit has not been successfully written since reset, then the read of the bit returns the reset value if there is one, or otherwise returns an UNKNOWN value.
        - A direct write to the bit must update a storage location associated with the bit.
        - While the use of the register is such that the bit is described as RES0, the value of the bit must have no effect on the operation of the PE, other than determining the value read back from that bit, unless this Manual explicitly defines additional properties for the bit.

        Considering only contexts that apply to a particular implementation, if there is a context in which a bit is defined as RES0, another context in which the same bit is defined as RES1, and no context in which the bit is defined as a functional bit, then it is IMPLEMENTATION DEFINED whether:

        - Writes to the bit are ignored, and reads of the bit return an UNKNOWN value.
        - The value of the bit can be written, and a read returns the last value written to the bit.

    The RES0 description can apply to bits or fields that are read-only, or are write-only:

    - For a read-only bit, RES0 indicates that the bit reads as 0, but software must treat the bit as UNKNOWN.
    - For a write-only bit, RES0 indicates that software must treat the bit as [SBZ](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadfaib).

    A bit that is RES0 in a context is reserved for possible future use in that context. To preserve forward compatibility, software:

    - Must not rely on the bit reading as 0.
    - Must use an [SBZP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadiida) policy to write to the bit.

    The definition of a RES0 field in an architecturally-defined data structure that is held in memory is:

    - A read of a RES0 bit returns the value last written.
    - The value of a RES0 bit has no effect on the operation of the PE or any other hardware implementing the architecture such as the GIC or the SMMU, other than determining the value read back from that bit, unless this Manual explicitly defines additional properties for the bit.
    - For an implicit memory write effect to the field by a PE or for a write to the field by any other hardware implementing the architecture such as the GIC or the SMMU, each bit defined as RES0 is set to 0.
    - For a write to the data structure by a PE, or any other hardware implementing the architecture such as the GIC or the SMMU, if the write is specified to only update specific fields, the hardware preserves the value of other RES0 bits in the same data structure. This applies, for example, to Hardware updates to the translation tables.

    This RES0 description can apply to a single bit, or to a field for which each bit of the field must be treated as RES0.

    In body text, the term RES0 is shown in SMALL CAPITALS.

    See also [Read-As-Zero (RAZ)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbdfbe), [RES0H](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaccdaea3), [RES1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadihjb), [Should-Be-Zero-or-Preserved (SBZP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babiiibg), [UNKNOWN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfcabf).

RES0H
:   A reserved bit or field with [SBZP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadiida). This behavior uses the hardwired to 0 subset of the RES0 definition.

    See also [Read-As-Zero (RAZ)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbdfbe), [RES0](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahedde), [RES1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadihjb), [Should-Be-Zero-or-Preserved (SBZP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babiiibg).

RES1
:   A reserved bit. Used for fields in register descriptions, and for fields in architecturally-defined data structures that are held in memory, for example in translation table descriptors.

    Within the architecture, there are some cases where a register bit or field:

    - Is RES1 in some defined architectural context.
    - Has different defined behavior in a different architectural context.

    > #### Note
    >
    > - RES1 is not used in descriptions of instruction encodings.
    > - Where an AArch32 System register is [Architecturally mapped](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadchjc) to an AArch64 System register, and a bit or field in that register is RES1 in one Execution state and has defined behavior in the other Execution state, this is an example of a bit or field with behavior that depends on the architectural context.

    This means the definition of RES1 for fields in read/write registers is:

    If a bit is RES1 in all contexts
    :   For a bit in a read/write register, it is IMPLEMENTATION DEFINED whether:

        1. The bit is hardwired to 1. In this case:

           - Reads of the bit always return 1.
           - Writes to the bit are ignored.
        2. The bit can be written. In this case:

           - An indirect write to the register sets the bit to 1.
           - A read of the bit returns the last value successfully written, by either a direct or an indirect write, to the bit.

             If the bit has not been successfully written since reset, then the read of the bit returns the reset value if there is one, or otherwise returns an UNKNOWN value.
           - A direct write to the bit must update a storage location associated with the bit.
           - The value of the bit must have no effect on the operation of the PE, other than determining the value read back from the bit, unless this Manual explicitly defines additional properties for the bit.

        Whether RES1 bits or fields follow behavior [1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafadej) or behavior [2](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbacgdbg) is IMPLEMENTATION DEFINED on a bit-by-bit basis.

    If a bit is RES1 only in some contexts
    :   For a bit in a read/write register, when the bit is described as RES1:

        - An indirect write to the register sets the bit to 1.
        - A read of the bit must return the value last successfully written to the bit, regardless of the use of the register when the bit was written.

          > #### Note
          >
          > As indicated in this list, this value might be written by an indirect write to the register.

          If the bit has not been successfully written since reset, then the read of the bit returns the reset value if there is one, or otherwise returns an UNKNOWN value.
        - A direct write to the bit must update a storage location associated with the bit.
        - While the use of the register is such that the bit is described as RES1, the value of the bit must have no effect on the operation of the PE, other than determining the value read back from that bit, unless this Manual explicitly defines additional properties for the bit.

        Considering only contexts that apply to a particular implementation, if there is a context in which a bit is defined as RES0, another context in which the same bit is defined as RES1, and no context in which the bit is defined as a functional bit, then it is IMPLEMENTATION DEFINED whether:

        - Writes to the bit are ignored, and reads of the bit return an UNKNOWN value.
        - The value of the bit can be written, and a read returns the last value written to the bit.

    The RES1 description can apply to bits or fields that are read-only, or are write-only:

    - For a read-only bit, RES1 indicates that the bit reads as 1, but software must treat the bit as UNKNOWN.
    - For a write-only bit, RES1 indicates that software must treat the bit as [SBO](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbagbjei).

    A bit that is RES1 in a context is reserved for possible future use in that context. To preserve forward compatibility, software:

    - Must not rely on the bit reading as 1.
    - Must use an [SBOP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadjhga) policy to write to the bit.

    The definition of a RES1 field in an architecturally-defined data structure that is held in memory is:

    - A read of a RES1 bit returns the value last written.
    - The value of a RES1 bit has no effect on the operation of the PE or any other hardware implementing the architecture such as the GIC or the SMMU, other than determining the value read back from that bit, unless this Manual explicitly defines additional properties for the bit.
    - For an implicit memory write effect to the field by a PE or for a write to the field by any other hardware implementing the architecture such as the GIC or the SMMU, each bit defined as RES1 is set to 1.
    - For a write to the data structure by a PE, or any other hardware implementing the architecture such as the GIC or the SMMU, if the write is specified to only update specific fields, the hardware preserves the value of other RES1 bits in the same data structure. This applies, for example, to Hardware updates to the translation tables.

    This RES1 description can apply to a single bit, or to a field for which each bit of the field must be treated as RES1.

    In body text, the term RES1 is shown in SMALL CAPITALS.

    See also [Read-As-One (RAO)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babeajdc), [RES0](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahedde), [RES0H](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaccdaea3), [Should-Be-One-or-Preserved (SBOP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babghfch), [UNKNOWN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfcabf).

Reserved
:   Unless otherwise stated:

    - Instructions that are reserved or that access reserved registers have UNPREDICTABLE or CONSTRAINED UNPREDICTABLE behavior.
    - Bit positions described as reserved are:

      - In an RW or WO register, RES0.
      - In an RO register, UNK.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [RES0](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahedde), [RES0H](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaccdaea3), [RES1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadihjb), [UNDEFINED](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjgjah), [UNK](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcbdab), [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Resource partition
:   The collection of MPAM resource control settings associated with a software environment and identified by the combination of a physical PARTID space and a partition number.

RESS
:   Reserved, Sign extended. A register value is extended by copying the sign bit into all of the reserved bits to the left of the most significant bit of the field. The values of these bits are identical to the most significant bit of the value being extended.

    Within the architecture, a register bit or field can be treated:

    - As RESS in few defined architectural contexts.
    - In a different defined behavior in other architectural contexts.

    This means the definition of RESS for fields in read/write registers is:

    If a field [Q:P] is RESS in all contexts
    :   For a bit in a read/write register, it is IMPLEMENTATION DEFINED whether:

        1. The bit is hardwired as a sign-extension of bit [P-1]. In this case:

           - Reads of the bit always return the value of bit [P-1].
           - Writes to the bit are ignored.
        2. The bit can be written. In this case:

           - An indirect write to the register sets the bit to the same value as bit [P-1].
           - A read of the bit returns the last value successfully written, by either a direct or an indirect write, to the bit.

             If the bit has not been successfully written since reset, then the read of the bit returns the reset value if there is one, or otherwise returns an UNKNOWN value.
           - A direct write to the bit must update a storage location associated with the bit.
           - The value of the bit must have no effect on the operation of the PE, other than determining the value read back from the bit, unless this Manual explicitly defines additional properties for the bit.

        Whether RESS bits or fields follow behavior 1 or behavior 2 is IMPLEMENTATION DEFINED on a bit-by-bit basis.

    If a field [Q:P] is RESS only in some contexts
    :   For a bit in a read/write register, when the bit is described as RESS:

        - An indirect write to the register sets the bit to the same value as bit [P-1].
        - A read of the bit must return the value last successfully written to the bit, regardless of the use of the register when the bit was written.

          > #### Note
          >
          > As indicated in this list, this value might be written by an indirect write to the register.

          If the bit has not been successfully written since reset, then the read of the bit returns the reset value if there is one, or otherwise returns an UNKNOWN value.
        - A direct write to the bit must update a storage location associated with the bit.
        - While the use of the register is such that the bit is described as RESS, the value of the bit must have no effect on the operation of the PE, other than determining the value read back from that bit, unless this Manual explicitly defines additional properties for the bit.

        Considering only contexts that apply to a particular implementation, if there is a context in which a bit is defined as RES0, another context in which the same bit is defined as RES1, and no context in which the bit is defined as a functional bit, then it is IMPLEMENTATION DEFINED whether:

        - Writes to the bit are ignored, and reads of the bit return an UNKNOWN value.
        - The value of the bit can be written, and a read returns the last value written to the bit.

    The RESS description can apply to bits or fields that are read-only, or are write-only:

    - For a read-only bit, RESS indicates that the bit reads as the value of bit [P-1], but software must treat the bit as UNKNOWN.
    - For a write-only bit, RESS indicates that software must treat the bit as [SBO](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbagbjei) or [SBZ](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadfaib) as necessary.

    A bit that is RESS in a context is reserved for possible future use in that context. To preserve forward compatibility, software:

    - Must not rely on the bit reading as [P-1].
    - Must use a [SBOP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadjhga) or [SBZP](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadiida) policy to write to the bit.

    This RESS description can apply to a single bit, or to a field for which each bit of the field must be treated as RESS.

Rewind point
:   A rewind point is a point in the program flow to which execution can return if all subsequent execution is found to have been incorrectly speculatively executed.

RISC
:   Reduced Instruction Set Computer.

RIS
:   Resource instance selection. The value in MPAMCFG\_PART\_SEL.RIS selects the resource instance that is configured through MPAMCFG\_\* registers and described by the MPAMF ID registers.

RME
:   Realm Management Extension.

Rounding error
:   The value of the rounded result of an arithmetic operation minus the exact result of the operation.

Rounding mode
:   Specifies how the exact result of a floating-point operation is rounded to a value that is representable in the destination format. The rounding modes are defined by the *IEEE Standard for Floating-point Arithmetic*, see [Floating-point standards, and terminology](/documentation/ddi0487/mc/-Part-A-Arm-Architecture-Introduction-and-Overview/-Chapter-A1-Introduction-to-the-Arm-Architecture/-A1-5-Floating-point-support/-A1-5-2-Floating-point-standards--and-terminology?lang=en#cacjfaig).

Saturated arithmetic
:   Integer arithmetic in which a result that would be greater than the largest representable number is set to the largest representable number, and a result that would be less than the smallest representable number is set to the smallest representable number. Signed saturated arithmetic is often used in DSP algorithms. It contrasts with the normal signed integer arithmetic used in Arm processors, in which overflowing results wrap around from +231-1 to -231 or vice versa.

SBO
:   See [Should-Be-One (SBO)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdggih).

SBOP
:   See [Should-Be-One-or-Preserved (SBOP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babghfch).

SBZ
:   See [Should-Be-Zero (SBZ)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babhdfce).

SBZP
:   See [Should-Be-Zero-or-Preserved (SBZP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babiiibg).

Scalable vector register
:   An SVE scalable vector register, Z0-Z31, having a length that is a power of two, in the range 128 bits to 2048 bits, inclusive.

Scalar base register
:   A scalar base register refers to an AArch64 general-purpose register, X0-X30, or the current stack pointer, SP.

Scalar index register
:   A scalar index register refers to an AArch64 general-purpose register, X0-X30, or for certain instructions, XZR.

Scalable Matrix Extension
:   Defines architectural state capable of holding two-dimensional matrix tiles, and a Streaming SVE mode which supports execution of SVE2 instructions with a vector length that matches the tile width, along with instructions that accumulate the outer product of two vectors into a tile, as well as load, store, and move instructions that transfer a vector to or from a tile row or column.

    See [The Scalable Matrix Extension](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D22-The-Scalable-Matrix-Extension?lang=en#cachgchbg5).

Scalable Matrix Extension version 2
:   Extends the Scalable Matrix Extension by adding data-processing instructions with multi-vector operands and amulti-vector predication mechanism, a lookup table feature, a binary outer product instruction, and a range prefetch hint.

    See [SME2 Multi-vector operands](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-12-SME2-Multi-vector-operands?lang=en#beifgbiga7), [Vector predication](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-5-Vector-predication?lang=en#beicjehdj1), and [SME2 ZT0 register](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-13-SME2-ZT0-register?lang=en#beicdfdef8).

Scatter-store
:   Scatter-store is a mechanism that allows the elements of a vector to be written to non-contiguous memory locations using a vector of addresses, where the addresses are constructed according to the addressing mode.

SDC
:   See [Silent Data Corruption (SDC)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdchjjdc6).

SDC FIT rate
:   The FIT rate for failures because of SDC.

SDEC
:   Single device error correction EDAC. This can detect and correct multiple clustered errors in a protection granule, such as the types of errors that might be seen if a protection granule is striped across multiple devices and multiple errors come from a single device.

SECDED
:   Single error correct, double error detect EDAC. This can detect a single or double bit error and correct a single bit error in a protection granule.

SED
:   Single error detect EDC. This can detect a single bit error in a protection granule.

Security hole
:   A mechanism by which execution at the current level of privilege can achieve an outcome that cannot be achieved at the current or a lower level of privilege using instructions that are not UNPREDICTABLE and are not CONSTRAINED UNPREDICTABLE. The Arm architecture forbids security holes.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Self-modifying code
:   Code that writes one or more instructions to memory and then executes them. When using self-modifying code, you must use cache maintenance and barrier instructions to ensure synchronization. For more information, see [Caches and memory hierarchy](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-7-Caches-and-memory-hierarchy?lang=en#chddgjhd).

SError exception
:   An asynchronous exception in the Arm architecture.

Serviceability
:   The ability to undergo modifications and repairs.

Service failure mode
:   A mode entered to reduce the severity of an error.

Set
:   See [Cache sets](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babhehad).

Should-Be-One (SBO)
:   Hardware must ignore writes to the field.

    Arm strongly recommends that software writes the field as all 1s. If software writes a value that is not all 1s, it must expect an UNPREDICTABLE or CONSTRAINED UNPREDICTABLE result.

    This description can apply to a single bit that should be written as 1, or to a field that should be written as all 1s.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Should-Be-One-or-Preserved (SBOP)
:   From the introduction of the Armv8 architecture, the description [Should-Be-One-or-Preserved (SBOP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babghfch) is superseded by [RES1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadihjb).

    Hardware must ignore writes to the field.

    When writing this field, software must either write all 1s to this field or, if the register is being restored from a previously read state, write the previously read value to this field. If this is not done, then the result is unpredictable.

    This description can apply to a single bit that should be written as its preserved value or as 1, or to a field that should be written as its preserved value or as all 1s.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Should-Be-Zero (SBZ)
:   Hardware must ignore writes to the field.

    Arm strongly recommends that software writes the field as all 0s. If software writes a value that is not all 0s, it must expect an UNPREDICTABLE or CONSTRAINED UNPREDICTABLE result.

    This description can apply to a single bit that should be written as 0, or to a field that should be written as all 0s.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Should-Be-Zero-or-Preserved (SBZP)
:   From the introduction of the Armv8 architecture, the description [Should-Be-Zero-or-Preserved (SBZP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babiiibg) is superseded by [RES0](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahedde).

    Hardware must ignore writes to the field.

    When writing this field, software must either write all 0s to this field or, if the register is being restored from a previously read state, write the previously read value to this field. If this is not done, then the result is unpredictable.

    This description can apply to a single bit that should be written as its preserved value or as 0, or to a field that should be written as its preserved value or as all 0s.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Signaling NaN
:   An Invalid Operation floating-point exception occurs whenever any floating-point operation receives a signaling NaN as an operand. Signaling NaNs can be used in debugging, to track down some uses of uninitialized variables.

    See also [NaN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbabcdaj), [Quiet NaN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbabfcaf).

Signed immediate and offset fields
:   Are encoded in two’s complement notation unless otherwise stated.

Silent Data Corruption (SDC)
:   An error that is not detected by hardware or software.

SIMD
:   Single-Instruction, Multiple-Data.

    The SIMD instructions in AArch32 state are:

    - The instructions summarized in [Parallel addition and subtraction instructions](/documentation/ddi0487/mc/-Part-F-The-AArch32-Instruction-Sets/-Chapter-F2-The-AArch32-Instruction-Sets-Overview/-F2-4-Data-processing-instructions/-F2-4-7-Parallel-addition-and-subtraction-instructions?lang=en#chdfjabe).
    - The Advanced SIMD instructions summarized in [Advanced SIMD and floating-point instructions](/documentation/ddi0487/mc/-Part-E-The-AArch32-Application-Level-Architecture/-Chapter-E1-The-AArch32-Application-Level-Programmers--Model/-E1-3-Advanced-SIMD-and-floating-point-instructions?lang=en#cfieafeb), when operating on vectors.

Simple sequential execution
:   The behavior of an implementation that fetches, decodes and completely executes each instruction before proceeding to the next instruction. Such an implementation performs no speculative accesses to memory, including to instruction memory. The implementation does not pipeline any phase of execution. In practice, this is the theoretical execution model that the architecture is based on, and Arm does not expect this model to correspond to a realistic implementation of the architecture.

Single-copy atomicity
:   The form of atomicity described in [Properties of single-copy atomic accesses](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B2-The-AArch64-Application-Level-Memory-Model/-B2-2-Atomicity-in-the-Arm-architecture/-B2-2-2-Properties-of-single-copy-atomic-accesses?lang=en#chdhgeie).

    See also [Atomicity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babefgdg), [Multi-copy atomicity](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcicag).

Single-precision value
:   A 32-bit word that is interpreted as a basic single-precision floating-point number according to the *IEEE Standard for Floating-point Arithmetic*.

SMCU
:   See [Streaming Mode Compute Unit](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdiagfeg1).

SME
:   See [Scalable Matrix Extension](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdcfagbg7).

SME2
:   See [Scalable Matrix Extension version 2](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdgjghhb2).

SMMU
:   System Memory Management Unit.

SPE
:   Statistical Profiling Extension.

Spatial locality
:   The observed effect that after a program has accessed a memory location, it is likely to also access nearby memory locations in the near future. Caches with multi-word cache lines exploit this effect to improve performance.

Special-purpose register
:   One of a specified set of registers for which all direct and indirect reads and writes to the register appear to occur in program order relative to other instructions, without the need for any explicit synchronization:

    - [Special purpose registers](/documentation/ddi0487/mc/-Part-C-The-AArch64-Instruction-Set/-Chapter-C5-The-A64-System-Instruction-Class/-C5-2-Special-purpose-registers?lang=en#aarch64_operations_special_purpose_registers) specifies the AArch64 Special-purpose registers.
    - [AArch32 general-purpose registers, the PC, and the Special-purpose registers](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-10-AArch32-general-purpose-registers--the-PC--and-the-Special-purpose-registers?lang=en#chdceeeed0) lists the AArch32 Special-purpose registers.

Speculative
:   A speculative operation is any of the following:

    - An operation performed by the PE before the PE has determined that the operation is required to be performed in a simple sequential execution.
    - An operation performed by the PE that is not required to be performed in a simple sequential execution.
    - An operation performed by the PE before the PE has architecturally resolved the architectural state of inputs or outputs of the operation.

    Examples of speculative operations are:

    - Operations that are generated by instructions that appear in the Execution stream after a branch that is not architecturally resolved.
    - Operations that are generated by instructions that appear in the Execution stream after an instruction where a synchronous exception condition has not been architecturally resolved.
    - Operations that are generated by conditional instructions for which the conditions for the instruction have not been architecturally resolved.
    - Operations that are generated by instructions that appear in the Execution stream after the point at which a precise asynchronous exception will be taken.
    - Operations generated by instructions for which one or more of the arguments come from a register that has not been architecturally resolved.
    - Operations generated by the hardware that are not directly generated by any instructions appearing in the Execution stream.
    - A memory effect (M2) that appears in program order after a memory effect (M1) where all of the following apply:

      - M1 is locally-ordered-before M2.
      - M1 has not been architecturally resolved.
    - Read accesses generated for a translation table walk for which the granule protection check for the address being accessed has not been architecturally resolved.

    See also [Execution stream](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbabdgfa).

SPI
:   Shared Peripheral Interrupt.

Streaming execution
:   Execution of instructions by a PE when that PE is in Streaming SVE mode.

    See [Streaming SVE mode](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-6-Streaming-SVE-mode?lang=en#beigieigd1).

Streaming Mode Compute Unit
:   Where more than one PE shares resources for Streaming execution of SVE and SME instructions, those shared resources are called a Streaming Mode Compute Unit (SMCU).

    See [Streaming execution priority](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D22-The-Scalable-Matrix-Extension/-D22-4-Streaming-execution-priority?lang=en#babieahhc0).

Streaming SVE mode
:   An execution mode that supports a substantial subset of the SVE2 instruction set and architectural state with a vector length that matches the width of SME tiles, which may be different from the vector length when the PE is not in Streaming SVE.

    See [Streaming SVE mode](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-6-Streaming-SVE-mode?lang=en#beigieigd1).

Streaming SVE register state
:   The registers *Z0-Z31*, *P0-P15*, and *FFR* that are accessed by SVE and SME instructions when the PE is in Streaming SVE mode.

    See [Streaming SVE mode](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-6-Streaming-SVE-mode?lang=en#beigieigd1).

Superpriority
:   An attribute that is used to denote virtual and physical IRQ and FIQ interrupts as non-maskable. IRQ and FIQ interrupts with Superpriority can be taken under certain conditions where usually they would be masked by the [PSTATE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D1-The-AArch64-System-Level-Programmers--Model/-D1-5-Process-state--PSTATE?lang=en#pstate).{I, F} bits.

SVL
:   See [Effective Streaming SVE vector length](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdgjcfid2).

System Control Processor
:   A PE dedicated to system control and monitoring.

T32 instruction ​
:   One or two halfwords that specify an operation to be performed by a PE that is executing in an Exception level that is using AArch32 and is in T32 state. T32 instructions must be halfword-aligned.

    T32 instructions were previously called Thumb instructions.

    See also [A32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahcjih), [A64 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaehged), [T32 state](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadecaf).

T32 state
:   The AArch32 Instruction set state in which the PE executes T32 instructions.

    T32 state was previously called Thumb state.

    See also [A32 state](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbaceeaf), [T32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafdiag).

Temporal locality
:   The observed effect that after a program has accesses a memory location, it is likely to access the same memory location again in the near future. Caches exploit this effect to improve performance.

Thumb instruction
:   See [T32 instruction](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbafdiag).

TLB
:   See [Translation Lookaside Buffer (TLB)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjbbcd).

TLB lockdown
:   A way to prevent specific translation table entries from being evicted from a TLB. This ensures that accesses to the associated regions of virtual memory never cause a translation table walk.

Translation context
:   The context information used to uniquely identify a cached copy of a translation. See [TLB maintenance](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D8-The-AArch64-Virtual-Memory-System-Architecture/-D8-17-TLB-maintenance?lang=en#mdsec_tlb_maintenance).

Translation Lookaside Buffer (TLB)
:   A microarchitectural structure containing the results of translation table walks. They help to reduce the average cost of a memory access.

Translation table
:   A table held in memory that defines the properties of regions of virtual memory.

Translation table walk
:   The process of doing a full translation table lookup. It is performed automatically by hardware.

Trap enable bits
:   In VFPv2, VFPv3U, and VFPv4U, determine whether trapped or untrapped exception handling is selected. If trapped exception handling is selected, the way it is carried out is IMPLEMENTATION DEFINED.

Unaligned
:   An unaligned access is an access where the address of the access is not aligned to the size of an element of the access.

Unaligned memory accesses
:   Are memory accesses that are not, or might not be, appropriately halfword-aligned, word-aligned, or doubleword-aligned.

Unallocated
:   Except where otherwise stated in this manual, an instruction encoding is unallocated if the architecture does not assign a specific function to the entire bit pattern of the instruction, but instead describes it as CONSTRAINED UNPREDICTABLE, UNDEFINED, UNPREDICTABLE, or as an unallocated hint instruction.

    A bit in a register is unallocated if the architecture does not assign a function to that bit.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [UNDEFINED](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjgjah), [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Uncontainable error
:   See [Uncontained error](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdjjhghf1).

Uncontained error
:   An error that has been, or might have been, silently propagated.

Uncorrected error
:   An error caused by a fault which was not removed.

UNDEFINED
:   Indicates cases where an attempt to execute a particular encoding bit pattern generates an exception, that is taken to the current Exception level, or to the default Exception level for taking exceptions if the UNDEFINED encoding was executed at EL0. This applies to:

    - Any encoding that is not allocated to any instruction.
    - Any encoding that is defined as never accessible at the current Exception level.
    - Some cases where an enable, disable, or trap control means an encoding is not accessible at the current Exception level.

    If the generated exception is taken to an Exception level that is using AArch32 then it is taken as an Undefined Instruction exception.

    > #### Note
    >
    > On reset, the default Exception level for taking exceptions from EL0 is EL1. However, an implementation might include controls that can change this, effectively making EL1 inactive. See the description of the Exception model for more information

    In body text, the term UNDEFINED is shown in SMALL CAPITALS.

    See also [Undefined Instruction exception](/documentation/ddi0487/mc/-Part-G-The-AArch32-System-Level-Architecture/-Chapter-G1-The-AArch32-System-Level-Programmers--Model/-G1-17-AArch32-state-exception-descriptions/-G1-17-1-Undefined-Instruction-exception?lang=en#cihcdfgc).

Undetected error
:   See [Latent error](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdiidgdi8).

Unified cache
:   Is a cache used for both processing instruction fetches and processing data loads and stores.

Unindexed addressing
:   Means addressing in which the base register value is used directly as the virtual address to send to memory, without adding or subtracting an offset. In most types of load/store instruction, unindexed addressing is performed by using offset addressing with an immediate offset of 0.

UNK
:   An abbreviation indicating that software must treat a field as containing an UNKNOWN value.

    Hardware must implement the bit as read as 0, or all 0s for a multi-bit field. Software must not rely on the field reading as zero.

    See also [UNKNOWN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfcabf).

UNK/SBOP
:   Hardware must implement the field as Read-As-One, and must ignore writes to the field.

    Software must not rely on the field reading as all 1s, and except for writing back to the register it must treat the value as if it is UNKNOWN. Software must use an SBOP policy to write to the field.

    This description can apply to a single bit that should be written as its preserved value or as 1, or to a field that should be written as its preserved value or as all 1s.

    See also [Read-As-One (RAO)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babeajdc), [Should-Be-One-or-Preserved (SBOP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babghfch), [UNKNOWN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfcabf).

UNK/SBZP
:   Hardware must implement the bit as Read-As-Zero, and must ignore writes to the field.

    Software must not rely on the field reading as all 0s, and except for writing back to the register must treat the value as if it is UNKNOWN. Software must use an SBZP policy to write to the field.

    This description can apply to a single bit that should be written as its preserved value or as 0, or to a field that should be written as its preserved value or as all 0s.

    See also [Read-As-Zero (RAZ)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babbdfbe), [Should-Be-Zero-or-Preserved (SBZP)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babiiibg), [UNKNOWN](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babfcabf).

UNKNOWN
:   An UNKNOWN value does not contain valid data, and can vary from implementation to implementation. An UNKNOWN value must not return information that cannot be accessed at the current or a lower level of privilege using instructions that are not UNPREDICTABLE, are not CONSTRAINED UNPREDICTABLE, and do not return UNKNOWN values.

    An UNKNOWN value can vary from moment to moment, and instruction to instruction, unless it has previously been assigned, other than at reset, to one of the following registers:

    - Any of the general-purpose registers.
    - Any of the Advanced SIMD and floating-point registers.
    - Any of the Scalable Vector Extension registers.
    - Any of the PSTATE N, Z, C, or V flags.

    An UNKNOWN value must not be documented or promoted as having a defined value or effect.

    In body text, the term UNKNOWN is shown in SMALL CAPITALS.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [UNDEFINED](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjgjah), [UNK](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcbdab), [UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjcgda).

Unpacked access
:   A memory access that is performed as a result of a load or store instruction for which the vector element size is larger than the memory element size.

Unpredicated instruction
:   An SVE instruction that does not have a Governing predicate operand and implicitly treats all other vector and predicate elements as Active.

UNPREDICTABLE
:   Means the behavior cannot be relied upon. UNPREDICTABLE behavior must not perform any function that cannot be performed at the current or a lower level of privilege using instructions that are not UNPREDICTABLE.

    UNPREDICTABLE behavior must not be documented or promoted as having a defined effect.

    An instruction that is UNPREDICTABLE can be implemented as UNDEFINED.

    Execution at Non-secure EL1 or EL0 of an instruction that is UNPREDICTABLE can be implemented as generating a trap exception that is taken to EL2, provided that at least one instruction that is not UNPREDICTABLE and is not CONSTRAINED UNPREDICTABLE causes a trap exception that is taken to EL2.

    In body text, the term UNPREDICTABLE is shown in SMALL CAPITALS.

    See also [CONSTRAINED UNPREDICTABLE](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdhgci), [UNDEFINED](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babjgjah).

Unrecoverable error
:   A contained error that is not recoverable. Continued correct operation is generally not possible. Usually this means correct operation of the system, but it can also be used in other contexts to describe correct operation of a smaller part. Systems might use high-level recovery techniques to work around an unrecoverable yet contained error in a component so that the system recovers from the error.

Upstream
:   The direction from Completers to Requesters.

VA
:   See [Virtual address (VA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babdadgb).

VFP
:   In Armv7, an extension to the Arm architecture, that provides single-precision and double-precision floating-point arithmetic.

Vector
:   A one-dimensional array of vector elements of the same size and data type.

Vector element
:   Individual subdivisions of a vector register that can be 8, 16, 32, 64 or 128 bits in size. The vector element size and data type is specified independently by each instruction.

Virtual address (VA)
:   An address generated by an Arm PE. This means it is an address that might be held in the program counter of the PE. For a PMSA implementation, the virtual address is identical to the physical address.

    See also [Intermediate physical address (IPA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babgfifb), [Physical address (PA)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babehcfi).

VL
:   See [Effective SVE vector length](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdgjajid0).

VM
:   Virtual Machine.

VMM
:   Virtual Machine Monitor. An alias for “hypervisor”.

Virtual PARTID
:   A PARTID in MPAM that can be used by a virtual machine (VM). Virtual PARTIDs are mapped into physical PARTIDs using the virtual partition mapping entries in the MPAMVPM0 - MPAMVPM7 registers.

Watchpoint
:   A debug event triggered by an access to memory, specified in terms of the address of the location in memory being accessed.

Way
:   See [Cache way](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babiihca).

WI
:   Writes Ignored. In a register that software can write to, a WI attribute applied to a bit or field indicates that the bit or field ignores the value written by software and retains the value it had before that write.

    See also [RAO/WI](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahcdee), [RAZ/WI](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbagjhaj), [RES0](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbahedde), [RES1](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#cbadihjb).

Word
:   A 32-bit data item. Words are normally word-aligned in Arm systems.

Word-aligned
:   Means that the address is divisible by 4.

Write-allocate cache
:   A cache in which a cache miss on storing data causes a cache line to be allocated into the cache.

Write-back cache
:   A cache in which when a cache hit occurs on a write access, the data is only written to the cache. Data in the cache can therefore be more up-to-date than data in the next level of cache or memory. Any such data is written back to the next level of cache or memory when the cache line is cleaned. Another common term for a write-back cache is a *copy-back cache*.

Write-One-to-Clear (W1C)
:   Writes of 0 to the bit are ignored. A write of 1 clears the bit to 0.

Write-One-to-Set (W1S)
:   Writes of 0 to the bit are ignored. A write of 1 sets the bit to 1.

Write-Through cache
:   A cache in which when a cache hit occurs on a write access, the data is written both to the cache and to the next level of cache or memory.

Write buffer
:   A block of high-speed memory that optimizes stores to main memory.

ZA array
:   A two-dimensional array of [SVLB × SVLB] bytes contained within the [ZA storage](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdiacaic1).

    See [ZA storage](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-8-ZA-storage?lang=en#beibbjiba1).

ZA array vector
:   A one-dimensional vector that is SVL bits in size within the [ZA array](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdghddah7).

    See [ZA array vector access](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-9-ZA-array-vector-access?lang=en#beibdhbaa3).

ZA storage
:   Architectural state added by SME that is capable of holding two-dimensional matrix tiles.

    See [ZA storage](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-8-ZA-storage?lang=en#beibbjiba1).

ZA tile
:   A square, two-dimensional sub-array of elements within the [ZA array](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdghddah7).

    See [ZA tile access](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-10-ZA-tile-access?lang=en#beicceced9).

ZA tile slice
:   A one-dimensional set of horizontally or vertically contiguous elements within a [ZA tile](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#chdbdjjdf0).

    See [ZA tile access](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-10-ZA-tile-access?lang=en#beicceced9).

Zeroing predication
:   When a predicated instruction specifies zeroing predication, the Inactive elements of the destination register are set to zero.

ZT0 register
:   The 512-bit architectural register added by SME2 that consists of up to sixteen 32-bit table entries, each containing an 8-bit, 16-bit, or 32-bit element.

    See [SME2 ZT0 register](/documentation/ddi0487/mc/-Part-B-The-AArch64-Application-Level-Architecture/-Chapter-B1-The-AArch64-Application-Level-Programmers--Model/-B1-4-The-Scalable-Vector-and-Scalable-Matrix-Extensions--SVE---SME-/-B1-4-13-SME2-ZT0-register?lang=en#beicdfdef8).
