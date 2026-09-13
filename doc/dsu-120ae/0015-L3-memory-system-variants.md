# L3 memory system variants

Source: <https://developer.arm.com/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Cluster-configurations/L3-memory-system-variants>

### L3 memory system variants

By default the DynamIQ Shared Unit-120AE (DSU-120AE) is implemented with an L3 cache. Depending on your requirements, you can instead implement the DSU-120AE without an L3 cache.

There are two possible L3 memory system implementations:

L3 cache present
:   This is the default implementation. It provides the most functionality and is suitable for general-purpose workloads.

L3 cache not present
:   In this implementation, the L3 cache is not present but snoop filter and Snoop Control Unit (SCU) logic are present.

    This variant allows multiple cores in the cluster and manages the coherency between them. It supports other implementation options such as Accelerator Coherency Port (ACP), Peripheral Port, and AXI or CHI requester ports. Excluding the L3 cache RAMs saves layout area but performance of typical workloads is reduced. Therefore, Arm recommends that this variant is only used in specialized use cases, or when there is a system cache present that can be used by the cores.

For more information on how to implement the DSU-120AE with one of the L3 memory system variants, see the Configuration Guidelines chapter in Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.

### Related information

- [DynamIQ Shared Unit-120AE configuration options](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/DynamIQ-Shared-Unit-120AE-configuration-options?lang=en "You must configure the DynamIQ Shared Unit-120AE (DSU-120AE) RTL for your implementation requirements prior to hardware synthesis at build time configuration. Configuration for the DSU-120AE is carried out together with configuration for the cores in your cluster.")
- [DynamIQ Shared Unit-120AE features](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/DynamIQ-Shared-Unit-120AE-features?lang=en "Some features in the DynamIQ Shared Unit-120AE (DSU-120AE) are fixed and some features are optional. You can configure optional features in the RTL during build time configuration, to meet your requirements.")
