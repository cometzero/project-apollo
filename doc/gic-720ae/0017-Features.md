# Features

Source: <https://developer.arm.com/documentation/102666/0201/About-the-GIC-720AE/Features>

### Features

The GIC-720AE provides interrupt services and masking, registers and programming, interrupt grouping, security, performance monitoring, and error correction and detection.

### Interrupt services and masking

The GIC-720AE provides the following interrupt features:

- Support for the following interrupt types:
  - Up to 56000 physical Locality-specific Peripheral Interrupts (LPIs). A peripheral generates these interrupts by writing to a memory-mapped register in the GIC-720AE.
  - Direct injection of up to 56000 virtual LPIs for each virtual processing element (vPE), when the GIC is configured to support GICv4.1.
  - Up to 1984 Shared Peripheral Interrupts (SPIs) in groups of 32. Up to 960 of these 1984 SPIs can be assigned as real-time SPIs, to use with devices that require a deterministic interrupt latency response.
  - Up to 48 Private Peripheral Interrupts) (PPIs) that are independent for each core and can be programmed to support either edge-triggered or level-sensitive interrupts. If a GIC Cluster Interface (GCI) is configured to support real-time interrupts, then these PPIs have a deterministic interrupt latency response for the PEs on that GCI.
  - Up to 16 physical Software Generated Interrupts (SGIs) for each core, which the core generates through its GIC CPU interface. If a GCI is configured to support real-time interrupts, then these SGIs have a deterministic interrupt latency response for the PEs on that GCI.
  - Direct injection of up to 16 virtual SGIs for each vPE, when the GIC is configured to support GICv4.1.
  - Provides four logical views so that up to three different OSs within a system can be assigned a different view.
- Up to 32 Interrupt Translation Service (ITS) modules that provide device isolation and ID translation for message-based interrupts and enable virtual machines to program devices directly.
- Interrupt masking and prioritization with 32 priority levels, 5 bits for each interrupt.

### Registers and programming

The GIC-720AE provides the following programming features:

- Flexible affinity routing, using the Multiprocessor Identification Register (MPIDR) addresses, including support for four affinity levels (0-3).
- Single ACE5-Lite subordinate interface on each chip for programming of all registers but excluding the GITS\_TRANSLATER register in non-monolithic configurations. Each ITS has an optional ACE5-Lite subordinate interface for programming the GITS\_TRANSLATER register.
- Coherent view of SPI register data across multiple chips.

### Security

The GIC-720AE provides the following security features:

- A global Disable Security signal. The gicd\_ctlr\_ds signal enables support for systems without security support. If the GIC configuration supports multi view, then the GIC assigns one gicd\_ctlr\_ds[3:0] signal bit to each view.
- The following interrupt groups allow interrupts to target different Exception levels:
  - Group 0
  - Non-secure Group 1
  - Secure Group 1

  See [Interrupt groups and security](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/Interrupt-groups-and-security?lang=en "The GIC-720AE configures the interrupts that it receives into one of three groups. Each group determines the security status of an interrupt and how it is routed.") for more information about security and groupings.

For more information about Exception levels, see the [Arm® Architecture Reference Manual for A-profile architecture](https://developer.arm.com/documentation/ddi0487/la).

### Performance monitoring

The GIC-720AE provides Performance Monitoring Unit (PMU) counters with snapshot functionality.

### Error correction and containment

The GIC-720AE provides the following error correction features:

- Armv8.2 Reliability Accessibility Serviceability (RAS) architecture-compliant error reporting for:
  - Software access errors.
  - ITS command and translation errors.
  - Error Correcting Code (ECC) errors.
- Containment of errored interrupts, to enable software recovery where possible.
- Software mechanism to trigger and test the error recovery functionality.
- GIC Stream Protocol Validator (GSPV), which ensures that the GIC Cluster Interface (GCI) receives compliant AXI5-Stream protocol and GIC Stream protocol.

The PMU and RAS error records are in the GICP and GICT register spaces, respectively. If the Security state changes, these registers retain their contents unless the debug reset signal (dbg\_reset\_n) goes LOW.

### Error detection

GIC-720AE contains the following error detection features:

- Lock-step of GIC blocks.
- AMBA parity on ACE5-Lite, AXI5-Stream, APB5, Q-Channel and P-Channel interfaces.
- Duplicated reset and clock with consistency detection.
- Protected MBIST interface signals.
- DFT false activation detection.
- Duplicated interrupt and interrupt return wires with consistency detection.
- Interrupt wire, and check wire, consistency protection using lock-step, flop parity, and BIST.
- Real-time interrupt prioritization protection using a combination of techniques including lock-step, flop parity, duplication, and output checking using alternate logic.
- End-to-end CRC protection over AXI5-Stream.
- End-to-end CRC protection over the cross-chip interface, which is configured to be either AXI5-Stream or ACE5-Lite.
