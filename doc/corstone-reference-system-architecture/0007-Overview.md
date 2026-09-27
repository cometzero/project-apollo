# Overview

Source: <https://developer.arm.com/documentation/102803/latest/Overview>

### Overview

The Corstone Reference Systems Architecture Specification Ma1 specifies the architecture of a subsystem that integrates key components available from Arm that can be integrated into a larger system. This document describes a subsystem for Cortex-M processors that support MVE extensions. The subsystem forms the core of a full system and, to form a full system, extra system peripherals must be added as expansion to the subsystem.

- Cortex-M CPU Core with M-Profile Vector Extension (MVE), FPU, DSP extensions, Caches, TCMs and ETM. This revision of CRSAS Ma1 supports Cortex-M85 or Cortex-M55 processors
- Ethos NPU core currently supports Ethos-U55 processor
- Multiple banks of System Volatile Memory, for example SRAMs
- Memory Protection Controllers (MPC)
- Manager Security Controller (MSC)
- Exclusive Access Monitor (EAM)
- System interconnect
- Implementation Defined Attribution Unit (IDAU)
- CMSDK Timers and Watchdog timers
- Timestamp-based System Timers and Watchdog timers
- Subsystem Controllers for security and general system control
- CoreSight SoC-600M components
- Power Policy Units, Clock Controller and Low Power Interface interconnect components (PCK-600)

This specification does not include descriptions of other components that are not directly architecturally visible but are necessary to implement the system.

These components are integrated to implement CRSAS Ma1 with the following features:

- TrustZone® aware system, with the system segregated into Secure and Non-secure worlds.
- Support for flexible banked volatile memory. This provides flexibility for the integrator and implementor to trade off between cost, complexity, memory throughput, and power consumption.
- Configurability to allow several features within the system to be included or removed.
- Power Control infrastructure, with several pre-defined voltage and power domains.
- Each switchable power domain has local power policy control, and coordinates with other power domains through a centralized dependency control and/or power interfaces. This provides the system with an autonomous dynamic power control infrastructure that, while being software configurable, aims to minimize software interaction.
- Clock control infrastructure that supports high-level clock control including dynamic clock gating and provides clock request handshakes to clock generators.
- Comprehensive reset generation and control.
- A CoreSight SoC based debug infrastructure that supports a shared Debug Access Port and Trace Port, with support also for cross triggering.

This specification is implemented by the following Arm products:

- Corstone-310

- **[Document-specific conventions](/documentation/102803/0000/Overview/Document-specific-conventions?lang=en)**
   In addition to the Typographic Conventions section, there are document-specific conventions that apply.
- **[Compliance](/documentation/102803/0000/Overview/Compliance?lang=en)**
   The system architecture described in this document is designed to meet the following requirement:
- **[Topology](/documentation/102803/0000/Overview/Topology?lang=en)**
   This section describes the topology of CRSAS Ma1.
