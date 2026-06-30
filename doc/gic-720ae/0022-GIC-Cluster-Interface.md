# GIC Cluster Interface

Source: <https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/GIC-Cluster-Interface>

### GIC Cluster Interface

The GIC Cluster Interface (GCI) is responsible for PPIs and SGIs that are associated with its related cluster or group of cores.

The following figure shows the GCI. The figure does not show the protection signals that a configuration can include.

Figure 1. GCI

![The GCI connects up to a Distributor with an AXI5-Stream interface, and connects down to 3 clusters with GIC Stream interfaces. One cluster is in a different domain, so the path to that cluster includes an ADB and a CPUIF block. The GCI also contains a GSPV block.](images/0022-GIC-Cluster-Interface-img01.svg)

The GCI performs the following functions:

- Maintaining the SGI and PPI programming.
- Monitoring, and if necessary, synchronizing the PPI wires.
- Prioritizing SGIs, PPIs, and any other interrupts that are sent from the Distributor, and forwarding them to the core. When a GCI is configured to support real-time interrupts, it arbitrates with the Distributor to satisfy the real-time requirements of PPIs and SGIs. At reset, if [GICR\_FCTLR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FCTLR--Function-Control-Register?lang=en "This register controls the clock gate overrides, the denial of Q-Channel requests, and the scrubbing of all RAMs in the associated Redistributor. For real-time GCIs, it can also disable the combining of GIC Stream messages.").ECP ==1, then the GCI supports real-time interrupts.
- Maintaining the GIC Stream protocol and communicating with the cluster. The GIC Stream Protocol Validator (GSPV) corrects any errors in the GIC Stream transfers. The GSPV supports mixed criticality systems where some processors might not have an ASIL-D rating.

A CPU interface (CPUIF) protection block provides a CRC protected connection from GCI to core, when any of the following apply:

- The GCI is configured to support multiple buses.
- The connection to the core is not a simple point-to-point connection because it contains register slices, an AMBA Domain Bridge (ADB), or an unprotected interconnect.
- When the `structure` configuration parameter is set to `wrap`, and the GIC is configured to reduce the number of AXI5-Stream interfaces on the GCI. See [Hierarchy](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Hierarchy?lang=en "The hierarchy of the GIC components can be selected using the structure configuration parameter.") for information about the `structure` parameter.

When using CPUIF protection, the final point-to-point connection can be configured to use AMBA parity or no protection, although AMBA parity is recommended.

There can be multiple GCIs in a configuration and they can be sized to match your system. For example, if you have two clusters of eight cores, then you can have one GCI positioned next to each cluster. You can use a GCI for each cluster to reduce the PPI wiring and enable the GCI to be powered down with the cores for extra power savings. Alternatively, for a small system, combining all cores into one GCI might be the best solution. See Configuration options in the Arm® CoreLink™ GIC-720AE Generic Interrupt Controller Configuration and Integration Manual for more information.

The GCI (GICR) registers are programmed through the Distributor ACE5-Lite subordinate interface. The Distributor also contains the architectural LPI functionality.

### GSPV

The GIC Stream Protocol Validator (GSPV) prevents the GIC Cluster Interface (GCI) from receiving non-compliant protocol packets from a CPU by monitoring transactions on the GIC Stream interface, which is implemented using AXI5-Stream. GSPV supports mixed-criticality systems with lower ASIL CPUs.

GSPV detects both the AXI5-Stream protocol and the GIC Stream protocol violations. These include:

- Incomplete or stalled AXI5-Stream transactions
- Missing or unexpected GIC Stream transactions
- Transactions containing invalid protocol fields

Errors are reported to the FMU as either SM\_GSPV\_AXIT, for AXI5-Stream protocol violations, or SM\_GSPV\_PROTO, for GIC Stream protocol violations. The [GICR\_FLUSHR](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-FLUSHR--Flush-Register?lang=en "This register controls the recovery mode for the GIC Stream Protocol Validator (GSPV) in the GCI.") register provides GSPV configuration, reporting, and recovery.

The GSPV provides a recovery mechanism to recover PEs that do not respond to a [GICR\_WAKER](https://developer.arm.com/documentation/102666/0201/Programmers-model-for-GIC-720AE/Redistributor-registers-for-control-and-physical-LPIs-summary/GICR-WAKER--Power-Management-Control-Register?lang=en "This register controls whether the GIC-720AE can be powered down.").ProcessorSleep handshake. It should be possible to reset a failing core without impacting the other cores that connect to the GIC. This is particularly important in mixed-criticality systems containing lower integrity than ASIL-D CPUs. However, to achieve this recovery, you must insert the correct clock and reset boundaries to meet these reset requirements. In general, when resetting at the cluster level, the easiest way is to provide a separate GCI for each cluster with a clock and reset boundary between the GCI and GICD, which provides a clean point to reset.

### Local PE wake

If a GIC configuration has `ci_wake` == 1, then each GCI has cpu\_wake\_request signals for the PEs that connect to that GCI. This configuration setting places another set of wakeup signals close to the cores. To wake a PE, the system designer can choose to use the cpu\_wake\_request signals or the wake\_request signals from the Wake Request block.

When a system uses the cpu\_wake\_request signals, if the system is able to power down a GCI, the system designer must connect the corresponding wake\_request signals to a power controller. When the GCI is powered down, the cpu\_wake\_request signals can not wake the cores, but the use of the wake\_request signals enables all cores on that GCI to be woken. See also [Wake Request](https://developer.arm.com/documentation/102666/0201/Components-in-GIC-720AE/Wake-Request?lang=en "The Wake Request block converts AXI5-Stream wake requests into one wake_request signal for each core. Each wake_request signal connects to the system power controller.").

### Related concepts

- [PPIs](https://developer.arm.com/documentation/102666/0201/Operation-of-GIC-720AE/PPIs?lang=en "A Private Peripheral Interrupt (PPI) identifies an interrupt source, such as a timer, that is private to the core, and which is independent of the same source for another core. PPIs are typically used for peripherals that are tightly coupled to a particular core.")
