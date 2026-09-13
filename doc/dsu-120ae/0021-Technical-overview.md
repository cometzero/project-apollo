# Technical overview

Source: <https://developer.arm.com/documentation/107721/0001/Technical-overview>

### Technical overview

A DynamIQ Shared Unit-120AE (DSU-120AE) cluster-based system is also known as a DSU-120AE.

The DSU-120AE comprises two top-level modules, these are:

A module to form a DSU-120AE DynamIQ™ cluster
:   This module includes the
    cores,
    complexes and the
    DynamIQ™ cluster shared logic.

A separate module for the DebugBlock
:   Separating the debug components from the
    DSU-120AE DynamIQ™ cluster enables the debug components to be implemented in a separate power domain, or to be combined with an existing system power domain, allowing debug over power down.

All the main System on Chip (SoC) interfaces appear at the top level of the DSU-120AE. The DSU-120AE connects the cores and complexes to an external memory system and the rest of the SoC.
