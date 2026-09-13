# DynamIQ Shared Unit-120AE features

Source: <https://developer.arm.com/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/DynamIQ-Shared-Unit-120AE-features>

### DynamIQ™ Shared Unit-120AE features

Some features in the DynamIQ Shared Unit-120AE (DSU-120AE) are fixed and some features are optional. You can configure optional features in the RTL during build time configuration, to meet your requirements.

### Fault protection features

The DSU-120AE introduces the following additional fault protection features:

- Dual-Core Lock-Step (DCLS) support for fault protection
- Split-configuration, Lock-configuration, and Mixed-configuration support. Mixed-configuration allows for DCLS support to be pin configured and includes Lock-mode, Split-mode, and a Hybrid-mode for flexible fault protection level. DCLS also includes temporal delay support for temporal diversity.
- Fault Management Unit (FMU) support for fault reporting structure
- Interface protection for all external interfaces in Lock-configuration and Mixed-configuration, except for the non-safety related debug logic
- Register protection for software fault protection

### Cache features

The DSU-120AE has the following cache features:

- Optional unified 16-way set-associative L3 cache, configurable from 256KB to 32MB
- 64-byte cache lines
- L3 cache slice support, for improved bandwidth and cache RAM layout, up to eight slices supported
- L3 cache powerdown based either on cache slices or cache ways
- Cache partitioning support, compliant with Memory System Resource Partitioning and Monitoring (MPAM) architecture
- Error Correcting Code (ECC) protection on L3 cache RAM instances
- L3 cache system can be clocked at a rate synchronous to the external system interconnect or at integer multiples.
- Quick Nap support on the L3 data RAMs

### Coherency and snoop control

The DSU-120AE has the following coherency and snoop control features:

- Snoop Control Unit (SCU) maintains coherency and consistency in the memory system internal to the cluster, and (optionally) external to the cluster.
- SCU includes a set of snoop filters, automatically sized, one for each cache slice

### Cluster features

The DSU-120AE has the following cluster features:

- Support for Arm®v9.2-A architecture cores
- Support for up to two types of core, and a maximum of 14 cores in the cluster
- The DSU-120AE has an internal transport mechanism that is responsible for all communication between components in the design. The topology of the transport is deﬁned by the number of cores and number of L3 cache slices.
- Power Policy Units (PPUs) providing autonomous power management of the L3 cache and the cores
- Support for core pairs and complex pairs running independently at different frequencies and voltages known as Dynamic Voltage Frequency Scaling (DVFS). For cores in a complex, DVFS is only possible for the whole complex pair, not for individual cores.

### Interface features

The DSU-120AE has the following interface features:

- Optional AMBA 5 CHI Issue E 256-bit coherent requester bus interface, supports up to four CHI bus requester ports.
- Optional AMBA AXI5 Issue H 256-bit non-coherent manager bus interface, supports up to four AXI bus manager ports.
- Configurable address target group methodology for CHI and AXI bus manager ports. The address target groups are used to optimize the interconnect connectivity between the bus manager ports and the system.
- Optional 128-bit or 256-bit wide I/O-coherent Accelerator Coherency Port (ACP) interfaces based on AMBA ACE5-Lite. Supports up to two ACP interfaces.
- AMBA AXI5 utility bus providing programming interface to PPUs, and other system components.
- Optional peripheral port interface that is implemented as either an AXI 64-bit wide port, AXI 256-bit wide port, or CHI Issue E 256-bit wide port.
- Simplified system integration for interfaces, such as debug and trace, which are already in the correct clock domain at the output of the cluster.

### Debug and trace features

The DSU-120AE has the following debug and trace features:

- Debug-over-powerdown support
- CoreSight SoC-600 support for Embedded Trace Extension (ETE) and Cross Trigger Interface (CTI) for each core.
- Optional CoreSight Embedded Logic Analyzer (ELA)-600 support
  > ### Note
  >
  > The ELA-600 is licensed separately.

### Related information

- [DynamIQ Shared Unit-120AE configuration options](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/DynamIQ-Shared-Unit-120AE-configuration-options?lang=en "You must configure the DynamIQ Shared Unit-120AE (DSU-120AE) RTL for your implementation requirements prior to hardware synthesis at build time configuration. Configuration for the DSU-120AE is carried out together with configuration for the cores in your cluster.")
