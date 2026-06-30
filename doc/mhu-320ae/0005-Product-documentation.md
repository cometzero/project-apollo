# Product documentation

Source: <https://developer.arm.com/documentation/107612/0001/Overview-of-MHU-320AE/Product-documentation>

### Product documentation

Each MHU-320AE document is aimed at a particular audience and is associated with specific tasks in the design flow.

These documents do not reproduce information that is available in the Arm architecture and protocol specifications. For architecture and protocol information that relates to MHU-320AE, see the Useful resources section.

The MHU-320AE documentation comprises:

Technical Reference Manual
:   The Technical Reference Manual (TRM) describes the functionality and the effects of functional options on the behavior of MHU-320AE. This document is useful at all stages of the product design flow.

    The choices that are made in the design flow can mean that some behaviors that the TRM describes are not relevant. If you are programming MHU-320AE, then contact:

    - The implementer to determine:
      - The build configuration of the implementation
      - The integration, if any, that was performed before implementing MHU-320AE
    - The integrator to determine the pin configuration of the device that you use

Configuration and Integration Manual
:   The Configuration and Integration Manual (CIM) contains:

    - Descriptions of MHU-320AE features
    - Design‑time configuration options
    - Reset‑time configuration options
    - Available build configuration options and related considerations
    - Instructions for configuring the RTL with the build configuration options
    - Instructions for running test vectors
    - Sign-off processes for the configured design
    - Considerations when integrating MHU-320AE into your system

    The Arm product deliverables include reference scripts and information about using these scripts to implement your design. The reference methodology flows that Arm supplies are example reference implementations only. For EDA tool support, contact your EDA tool vendor.

    The CIM is a Confidential document that is only available to licensees of MHU-320AE.

Safety Manual
:   The Safety Manual (SM) provides additional information on specific features of MHU-320AE that are relevant to Functional Safety. This information is important for SoC integrators whose final designs target applications where Functional Safety is a concern. The SM is a confidential document that is only available to licensees.

Development Interface Report
:   The Development Interface Report (DIR) describes the activities conducted by Arm that are related to the safety architecture of MHU-320AE. The DIR is a confidential document that is only available to licensees.
