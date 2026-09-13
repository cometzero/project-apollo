# Design Tasks

Source: <https://developer.arm.com/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Design-Tasks>

### Design Tasks

Both the DynamIQ Shared Unit-120AE (DSU-120AE) and the cores in the cluster are delivered as synthesizable RTL descriptions in Verilog HDL. Before you can use the DSU-120AE and the cores, you must implement, integrate, and program them.

A different party can perform each of the following tasks. Each task can include implementation and integration choices that affect the behavior and features of the DSU-120AE and the cores.

Implementation
:   The implementer configures and synthesizes the RTL to produce a hard macrocell. This task includes integrating RAMs into the design.

Integration
:   The integrator connects the macrocell into a System on Chip (SoC). This task includes connecting the macrocell to the memory system and peripherals.

Programming
:   In the final task, the system programmer develops the software to configure and initialize the
    DSU-120AE and the
    cores in the cluster and tests the application software.

The operation of the final device depends on the following:

Build configuration
:   The implementer chooses the options that affect how the RTL source files are pre-processed.

    These options usually include or exclude logic that affects one or more of the area, maximum frequency, and features of the resulting macrocell.

Configuration inputs
:   The integrator configures some features of the DSU-120AE and cores in the cluster by tying inputs to specific values.

    These configuration settings affect the start-up behavior before any software configuration is made. They can also limit the options available to the software.

Software configuration
:   The programmer configures the
    DSU-120AE and the
    cores in the cluster by programming values into registers. The configuration choices affect the behavior of the
    DSU-120AE and the
    cores.

For implementation options, see the following:

- RTL configuration process in the Configuration and Integration Manual for your licensed core
- RTL configuration process in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual

### Related information

- [System control registers](/documentation/107721/0001/System-control-registers?lang=en "The system control registers control and provide status information for the functions that the DynamIQ Shared Unit-120AE (DSU-120AE) implements. They can be accessed from the cores directly or externally through the utility bus.")
