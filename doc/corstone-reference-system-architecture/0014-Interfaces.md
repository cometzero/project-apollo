# Interfaces

Source: <https://developer.arm.com/documentation/102803/latest/Interfaces>

### Interfaces

The subsystem has several interfaces. This section provides the associated properties of each interface such as address and data width, along with the clock, power and reset domain that each belongs to. Some interfaces are only required under certain configurations. It is IMPLEMENTATION DEFINED whether an interface which is not required is either:

- Not implemented
- Implemented but the signals are tied off

In this section, the following conventions are used:

AMBA Manager Interface
:   An AMBA interface that is described as a manager interface is one where the subsystem is the manager and must be connected to a subordinate interface.

    For an AXI manager interface the ARVALID signal is an output and ARREADY is an input.

    For an AHB manager interface the HADDR signal is an output and HRDATA is an input.

    For an APB manager interface, the PADDR signal is an output.

AMBA Subordinate Interface
:   An AMBA interface that is described as a subordinate interface is one where the subsystem is the subordinate and must be connected to a manager interface.

    For an AXI subordinate interface the ARVALID signal is an input and ARREADY is an output.

    For an AHB subordinate interface the HADDR signal is an input and HRDATA is an output.

    For an APB subordinate interface, the PADDR signal is an input.

LPI Control Interface
:   An LPI interface that is described as a control interface, is one where the subsystem is the device and must be connected to a control interface.

    For a Q-Channel control interface the QREQn signal is an input and QACCEPTn, QDENY, and QACTIVE are outputs.

    For a P-Channel control interface the PREQn signal is an input and PACCEPTn, PDENY, and PACTIVE are outputs.

LPI Device Interface
:   An LPI interface described as a device interface, is one where the subsystem is the controller and must be connected to a device interface.

    For a Q-Channel device interface the QREQn signal is an output and QACCEPTn, QDENY and QACTIVE are inputs.

    For a P-Channel device interface the PREQn signal is an output and PACCEPTn, PDENY and PACTIVE are inputs.

An implementation of CRSAS Ma1 can add additional interface as long as it does not affect the behavior of these interfaces. For example, the processor core used in this system often provides more processor state outputs. These can always be made available for expansion but their existence is IMPLEMENTATION DEFINED.

- **[Input and output clocks](/documentation/102803/0000/Interfaces/Input-and-output-clocks?lang=en)**
   The following table lists all the clock inputs into the subsystem.
- **[Functional reset inputs and outputs](/documentation/102803/0000/Interfaces/Functional-reset-inputs-and-outputs?lang=en)**
   Reset inputs are used to drive or to request for resets while reset outputs are used to reset expansion logic that resides in specific power domains. For more information, see [Reset infrastructure](/documentation/102803/0000/Functional-Description/Reset-infrastructure?lang=en "CRSAS Ma1 defines the following system level reset scopes, namely:").
- **[P-Channel and Q-Channel Device Interfaces](/documentation/102803/0000/Interfaces/P-Channel-and-Q-Channel-Device-Interfaces?lang=en)**
   Each P-Channel or Q-Channel Device Interface independently allows external expansion logic to handshake with the system to ensure that:
- **[Clock Control Q-Channel Control interfaces](/documentation/102803/0000/Interfaces/Clock-Control-Q-Channel-Control-interfaces?lang=en)**
   Each Q-Channel Control interface in this section is single bit per signal on the Q-Channel interface and independently allows the system to request for the availability of a clock source. Each Q-Channel Control interface allows an external clock controller to handshake with the system to safely turn the clock source OFF.
- **[Expansion Power Control Dependency interface](/documentation/102803/0000/Interfaces/Expansion-Power-Control-Dependency-interface?lang=en)**
   CRSAS Ma1 provides an optional set of 2, up to 4-bit width Q-Channel interfaces that allow external power domains to use the Power Dependency Control Matrix to keep power domains within the subsystem from entering a lower power state.
- **[Power Domain ON Status Signals](/documentation/102803/0000/Interfaces/Power-Domain-ON-Status-Signals?lang=en)**
   CRSAS Ma1 provides a set of output signals that indicates if the power domain each is associated with is in the ON Power Mode.
- **[System timestamp interface](/documentation/102803/0000/Interfaces/System-timestamp-interface?lang=en)**
   CRSAS Ma1 provides a system timestamp input from an expansion timestamp counter. This timestamp is expected to be driven by a timestamp generator in the subsystem expansion. This resides in the PD\_AON power domain and nWARMRESETAON reset domain.
- **[Main Interconnect Expansion interfaces](/documentation/102803/0000/Interfaces/Main-Interconnect-Expansion-interfaces?lang=en)**
   CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces of the Main Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system.
- **[Peripheral Interconnect Expansion interfaces](/documentation/102803/0000/Interfaces/Peripheral-Interconnect-Expansion-interfaces?lang=en)**
   CRSAS Ma1 provides a configurable number of Manager and Subordinate Expansion interfaces from the Peripheral Interconnect. These interfaces allow the system integrator to add additional bus managers and bus subordinates to the system that is expected to require lower latency access to peripherals.
- **[Interrupt interfaces](/documentation/102803/0000/Interfaces/Interrupt-interfaces?lang=en)**
   CRSAS Ma1 includes interrupt signals for use by the subsystem expansion. These connect to the interrupt controller of each CPU within the system and optionally to an External Wakeup Controller (EWIC) associated with the CPU or the Internal Wakeup Interrupt Controller (IWIC) of the CPU.
- **[DMA interfaces](/documentation/102803/0000/Interfaces/DMA-interfaces?lang=en)**
   CRSAS Ma1 supports a DMA in the system and when DMA exists, namely NUMDMA>1, the following interfaces can exist depending on the configuration of the DMA:
- **[CPU Coprocessor Interface](/documentation/102803/0000/Interfaces/CPU-Coprocessor-Interface?lang=en)**
   Each CPU core of the subsystem can be configured to have a coprocessor interface. If a CPU<n> coprocessor interface exists, then HASCPU<n>CPIF = 1.
- **[TCM subordinate interface](/documentation/102803/0000/Interfaces/TCM-subordinate-interface?lang=en)**
   A 64-bit subordinate TCM interface provides system access only to Tightly Coupled Memories (TCM) internal to each CPU. The protocol of this interface is IMPLEMENTATION DEFINED.
- **[Debug and Trace Related interfaces](/documentation/102803/0000/Interfaces/Debug-and-Trace-Related-interfaces?lang=en)**
   This section describes the debug and trace related interfaces of CRSAS Ma1.
- **[CryptoCell Related Expansion interfaces](/documentation/102803/0000/Interfaces/CryptoCell-Related-Expansion-interfaces?lang=en)**
   The following section details interfaces that must exist when HASCRYPTO = 1.
- **[Security Control Expansion signals](/documentation/102803/0000/Interfaces/Security-Control-Expansion-signals?lang=en)**
   CRSAS Ma1 provides additional status and control signals to handle additional Manager Security Controllers (MSC), Memory Protection Controllers (MPC), Peripheral Protection Controllers (PPC) and Bridges with write buffers in the expansion system. These signals allow all the components to be controlled using the same set of security control registers already implemented within the subsystem.
- **[Clock configuration interface](/documentation/102803/0000/Interfaces/Clock-configuration-interface?lang=en)**
   CRSAS Ma1 provides a set of control and status signals for some of the clocks to configure generators or dividers that might exist in the expansion system.
- **[Miscellaneous signals](/documentation/102803/0000/Interfaces/Miscellaneous-signals?lang=en)**
   The following are other signals available for CRSAS Ma1.
