# FuSa programmer's view

Source: <https://developer.arm.com/documentation/102666/0201/Functional-safety-in-GIC-720AE/FuSa-programmer-s-view>

### FuSa programmer's view

The FMU contains the functional safety registers.

The GIC-700 memory map that is used to address the non-fusa legacy GIC functional logic is unchanged on GIC-720AE. See [Programmers model for GIC-720AE](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE?lang=en "All the GIC-720AE registers have names that are constructed of mnemonics that indicate the logical block that the register belongs to and the register function.") for the functional GIC-700 memory map.

GIC-720AE uses a separate and independent memory map for the FMU programmer's view. For a description of the registers that are specific to GIC-720AE, see [FMU register summary](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/FMU-register-summary?lang=en "The GIC-720AE Fault Management Unit (FMU) functions are controlled through registers that are identified with the prefix FMU.").
