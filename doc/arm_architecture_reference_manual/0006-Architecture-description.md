# Architecture description

Source: <https://developer.arm.com/documentation/ddi0487/mc/Preface/About-this-Manual/Architecture-description>

##### Architecture description

The Arm® A-profile architecture describes the operation of an Armv8-A and an Armv9-A [*Processing element* (PE)](/documentation/ddi0487/mc/-Part-K-Appendixes/Glossary?lang=en#babcidja). This Manual includes descriptions of:

- The two Execution states, AArch64 and AArch32.
- The instruction sets:

  - In AArch32 state, the T32 and A32 instruction sets, which are compatible with earlier versions of the Arm architecture.
  - In AArch64 state, the A64 instruction set.
- The states that determine how a PE operates, including the current Exception level and Security state, and in AArch32 state the PE mode.
- The Exception model.
- The interprocessing model, that supports transitioning between AArch64 state and AArch32 state.
- The memory model, that defines memory ordering and memory management. This Manual covers the Arm A architecture profile, both Armv8-A and Armv9-A, that defines a *Virtual Memory System Architecture* (VMSA).
- The programmers’ model, and its interfaces to System registers that control most PE and memory system features, and provide status information.
- The Advanced SIMD and floating-point instructions, which provide high-performance:

  - Single-precision, half-precision, and double-precision floating-point operations.
  - Conversions between double-precision, single-precision, and half-precision floating-point values.
  - Integer, single-precision floating-point, and half-precision floating-point vector operations in all instruction sets.
  - Double-precision floating-point vector operations in the A64 instruction set.
- The security model, which provides up to four Security states to support Secure applications and confidential computing.
- The virtualization model.
- The Debug architecture, which provides software access to debug features.

This Manual gives the assembler syntax for the instructions it describes, meaning that it describes instructions in textual form. However, this Manual is not a tutorial for Arm assembler language, nor does it describe Arm assembler language, except at a basic level. To make effective use of Arm assembler language, read the documentation supplied with the assembler being used.

This Manual is organized into parts:

Part A
:   Provides an introduction to the Arm architecture, and an overview of the AArch64 and AArch32 Execution states.

Part B
:   Describes the application level view of the AArch64 Execution state, meaning the view from EL0. It describes the application level view of the programmers’ model and the memory model.

Part C
:   Describes the A64 instruction set, which is available in the AArch64 Execution state. The descriptions for each instruction also include the precise effects of each instruction when executed at EL0, described as *unprivileged* execution, including any restrictions on its use, and how the effects of the instruction differ at higher Exception levels. This information is of primary importance to authors and users of compilers, assemblers, and other programs that generate Arm machine code.

Part D
:   Describes the system level view of the AArch64 Execution state. It includes details of the System registers, most of which are not accessible from EL0, and the system level view of the programmers’ model and the memory model. This part includes the description of self-hosted debug.

Part E
:   Describes the application level view of the AArch32 Execution state, meaning the view from the EL0. It describes the application level view of the programmers’ model and the memory model.

    > #### Note
    >
    > In AArch32 state, execution at EL0 is execution in User mode.

Part F
:   Describes the T32 and A32 instruction sets, which are available in the AArch32 Execution state. These instruction sets are backwards-compatible with earlier versions of the Arm architecture. This part describes the precise effects of each instruction when executed in User mode, described as *unprivileged* execution or execution at EL0, including any restrictions on its use, and how the effects of the instruction differ at higher Exception levels. This information is of primary importance to authors and users of compilers, assemblers, and other programs that generate Arm machine code.

    > #### Note
    >
    > User mode is the only mode where software execution is unprivileged.

Part G
:   Describes the system level view of the AArch32 Execution state, which is generally compatible with earlier versions of the Arm architecture. This part includes details of the System registers, most of which are not accessible from EL0, and the instruction interface to those registers. It also describes the system level view of the programmers’ model and the memory model.

Part H
:   Describes the Debug architecture for external debug. This provides configuration, breakpoint and watchpoint support, and a *Debug Communications Channel* (DCC) to a debug host.

Part I
:   Describes additional features of the architecture that are not closely coupled to a PE, and therefore are accessed through memory-mapped interfaces. Some of these features are OPTIONAL.

Part J
:   Provides pseudocode that describes various features of the Arm architecture.

Part K, Appendixes
:   Provide additional information. Some appendixes give information that is not part of the A-profile architectural requirements. The cover page of each appendix indicates its status.

Glossary
:   Defines terms used in this Manual that have a specialized meaning.

    > #### Note
    >
    > Terms that are generally well understood in the microelectronics industry are not included in the Glossary.
