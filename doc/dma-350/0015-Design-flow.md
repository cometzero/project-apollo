# Design flow

Source: <https://developer.arm.com/documentation/102482/0000/DMA-350-overview/Product-documentation-and-design-flow/Design-flow>

### Design flow

The DMA-350 is delivered as synthesizable RTL. Before it can be used in a product, it must go through the following processes:

Implementation
:   The implementer configures and synthesizes the RTL to produce a soft netlist.

Integration
:   The integrator connects the implemented design into an SoC. Integration includes connecting the design to a memory system and peripherals.

Programming
:   The system programmer develops the software to configure and initialize the DMA-350, and tests the required application software.

    Each process is separate and can include implementation and integration choices that affect the behavior and features of the DMA-350.

The operation of the final device depends on:

Build configuration
:   The implementer chooses the options that affect how the RTL source files are pre-processed.

    These options usually include or exclude logic that affects one or more of the following:

    - Area
    - Maximum frequency
    - Features of the resulting macrocell

Configuration inputs
:   The integrator configures some features of the DMA-350 by tying inputs to specific values. These configurations affect the start-up behavior before any software configuration is made.

Software configuration
:   The programmer configures the DMA-350 by programming particular values into registers. This configuration affects the behavior of the DMA-350.
