# ACP subordinate interface

Source: <https://developer.arm.com/documentation/107721/0001/ACP-subordinate-interface>

### ACP subordinate interface

The Accelerator Coherency Port (ACP) is an optional subordinate interface that provides coherent transaction support between the DynamIQ Shared Unit-120AE (DSU-120AE) and external accelerators such as a Direct Memory Access (DMA) engine. Up to two ACP interfaces can be configured during build time configuration, with each ACP interface being implemented as either a 128-bit or 256-bit port.

The ACP subordinate interface allows an external manager to access memory through the main memory interface of the DSU-120AE. Accesses are optimized for cache line length.

To maintain cache coherency, accesses are checked in the L3 cache and in the data caches in each core.

By default, ACP write-accesses to cacheable memory are implicit stash requests to the L3 cache. Alternatively, explicit stash requests (WriteUniqueFullStash, WriteUniquePtlStash, StashOnceShared, or StashOnceUnique) can target the L2 cache of a selected core or the L3 cache.

> ### Note
>
> - You can configure the DSU-120AE to have an ACP port, when the L3 cache is not present. This configuration is only recommended if the ACP is used for cache stashing to L2 caches in the cores.
> - For information on the configuring the number of ACP interfaces, the ACP port width, and the placement of ACP interfaces in the DSU-120AE, see the RTL configuration process in the Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.

### Related information

- [ACP features](/documentation/107721/0001/ACP-subordinate-interface/ACP-features?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification and includes support for atomic transactions and cache stashing. Memory tagging is also supported but only to a basic level as defined by the AMBA specification. This allows reading and writing the tags but does not support tag matching on writes.")
- [ACP ACE5-LiteDVM protocol subset](/documentation/107721/0001/ACP-subordinate-interface/ACP-ACE5-LiteDVM-protocol-subset?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification that includes support for Cacheable, Non-cacheable, and Device memory accesses.")
- [ACP transactions](/documentation/107721/0001/ACP-subordinate-interface/ACP-transactions?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification. The ACP interface includes support for Cacheable, Non-cacheable, Device, and Atomic memory accesses.")
- [ACP performance](/documentation/107721/0001/ACP-subordinate-interface/ACP-performance?lang=en "For optimum performance, use the following guidelines for Accelerator Coherency Port (ACP) transactions.")
