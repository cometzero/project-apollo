# DynamIQ Shared Unit-120AE configuration options

Source: <https://developer.arm.com/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/DynamIQ-Shared-Unit-120AE-configuration-options>

### DynamIQ™ Shared Unit-120AE configuration options

You must configure the DynamIQ Shared Unit-120AE (DSU-120AE) RTL for your implementation requirements prior to hardware synthesis at build time configuration. Configuration for the DSU-120AE is carried out together with configuration for the cores in your cluster.

> ### Note
>
> For a complete list of the configuration parameters and guidelines, see
> RTL configuration process in
> Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual (
> DSU-120AE CIM).

The DSU-120AE configuration options include:

Number of cores
:   You can configure the cluster to have between
    two and 14
    cores. Each
    core within a
    complex counts towards the total number of
    cores in the cluster. This is in addition to any
    cores in the cluster that are not in
    complexes (stand-alone
    cores).

Core type
:   You can have a cluster that includes up to
    two different types of
    cores. See
    [Cluster configurations](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Cluster-configurations?lang=en "A cluster can be configured with up to two different types of cores in the same cluster, irrespective of whether the cluster is configured either for Lock-configuration or Mixed-configuration. Each core can target different power efficiency and performance levels. The cluster also supports complexes."), for more information on the types of
    core that are supported.

L3 cache size
:   You can configure the L3 cache size to be:

    - 0KB
    - 256KB
    - 512KB
    - 1MB
    - 1.5MB
    - 2MB
    - 3MB
    - 4MB
    - 6MB
    - 8MB
    - 12MB
    - 16MB
    - 24MB
    - 32MB
:   > ### Note
    >
    > Setting the size of 0KB implements the
    > DSU-120AE without an L3 cache, see
    > [L3 memory system variants](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/Cluster-configurations/L3-memory-system-variants?lang=en "By default the DynamIQ Shared Unit-120AE (DSU-120AE) is implemented with an L3 cache. Depending on your requirements, you can instead implement the DSU-120AE without an L3 cache.").

L3 cache slices
:   You can configure the
    DSU-120AE to have 1, 2, 4, or 8 cache slices. For more information on cache slices, see
    [Cache slices and power portions](/documentation/107721/0001/L3-cache/Cache-slices-and-power-portions?lang=en "The L3 cache of the DynamIQ Shared Unit-120AE (DSU-120AE) can be divided up into identical slices, up to a limit of eight slices, each containing between 256KB and 4MB of the cache. A cache slice consists of the data, tag, victim, and snoop filter RAMs and associated logic. A power portion is a further subdivision of RAM in a cache slice.").

Transport configuration
:   The topology of the transport mechanism is automatically determined, dependent on the number of
    cores and L3 cache slices in your cluster. However, you can set transport data path width. For information on the
    DSU-120AE transport, see
    RTL configuration process in
    Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.

Memory interface configuration
:   You can configure the main memory interface to either use a CHI coherent interface or an AXI non-coherent interface. For either type of memory interface, you can configure the
    DSU-120AE to have 1, 2, 3, or 4 bus
    manager interfaces.

ACP interface
:   You can include up to two Accelerator Coherency Port (ACP) interfaces and specify their size.

Peripheral port
:   You can include the peripheral port and specify its size. You can also configure it to be a non-coherent bus
    manager interface.

Timing closure
:   You can configure the L3 cache RAM timing latency and optionally include register slices.

ELA
:   Include support for integrating the CoreSight Embedded Logic Analyzer (ELA)-600 into the DSU-120AE.

    > ### Note
    >
    > The ELA-600 is licensed separately.

DCLS mode
:   Enables Dual-Core Lock-Step (DCLS) support. When this parameter is set to Lock-configuration or Mixed-configuration, the DCLS primary and redundant logic is present to support fault protection features.

    > ### Note
    >
    > When this parameter is set to
    > Split-configuration, no DCLS logic is included, and the design behaves similarly to the DynamIQ Shared Unit-120.

DCLS delays
:   Configures the temporal diversity between the
    primary and
    redundant logic. For more information about the
    `DCLS_DELAYS` values, see the
    Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual. For more information about temporal diversity, see
    [Mixed-configuration](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/DCLS-configurations/Mixed-configuration?lang=en "A third build-time DCLS configuration is called Mixed-configuration.").
