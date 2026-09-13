# Page-Based Hardware Attribute

Source: <https://developer.arm.com/documentation/107721/0001/Technical-overview/Interfaces/Page-Based-Hardware-Attribute>

### Page-Based Hardware Attribute

The Page-Based Hardware Attribute (PBHA) bits are provided by the cores, and passed on or preserved by the DynamIQ Shared Unit-120AE (DSU-120AE). PBHA is supported on all the manager ports, the AXI or CHI Peripheral port, and all the Accelerator Coherency Ports (ACPs).

The PBHA bits are provided externally as sideband signals on each of the supported PBHA busses, alongside manager requests. PHBA affects the following:

RAM sizes
:   To generate accurate PBHA bits on L3 cache evictions, the bits need to be stored in the L3 cache. This can be configured by setting the
    `L3_PBHA_STORAGE` configuration parameter. If this parameter is not set, the PBHA bits are only accurate for read transactions. If this is set, the width of all L3 tag RAM instances is increased by four bits.

ACP
:   The
    ARPBHAS and
    AWPBHAS signals provide the PBHA value for any ACP request.

Cache stash transactions on CHI
:   Cache stash transactions might be sent on the CHI interface. For these requests, the PBHA bits being used must be sent along with the stash snoop transaction. There are separate signals providing PBHA information for stashing snoops.

Transaction support
:   Transactions that do not have a physical address associated with them, for example Distributed Virtual Memory (DVM) messages, do not provide the PBHA bits. Evict transactions that do not provide any data (for use in de-allocating a snoop filter) do not provide PBHA bits.

Mismatched aliases
:   If the same physical address is accessed through more than one virtual address mapping, and the PBHA bits are different in the mappings, then the results are
    UNPREDICTABLE. The PBHA value sent on the bus could be for either mapping.

> ### Note
>
> For information on PBHA signals, see
> Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.

### Related information

- [DynamIQ Shared Unit-120AE configuration options](/documentation/107721/0001/The-DynamIQ-Shared-Unit-120AE/DynamIQ-Shared-Unit-120AE-configuration-options?lang=en "You must configure the DynamIQ Shared Unit-120AE (DSU-120AE) RTL for your implementation requirements prior to hardware synthesis at build time configuration. Configuration for the DSU-120AE is carried out together with configuration for the cores in your cluster.")
