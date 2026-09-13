# ACP ACE5-LiteDVM protocol subset

Source: <https://developer.arm.com/documentation/107721/0001/ACP-subordinate-interface/ACP-ACE5-LiteDVM-protocol-subset>

### ACP ACE5-LiteDVM protocol subset

The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification that includes support for Cacheable, Non-cacheable, and Device memory accesses.

The ACP interface supports the following features as defined in the AMBA ACE5-LiteDVM protocol specification:

- Normal Read-Allocate and Write-Allocate cacheable memory is supported.
- Normal Non-cacheable and Device memory accesses are supported.
- Atomics are supported.
- All requests can be Secure or Non-secure.
- All requests can specify Inner Shareable, Outer Shareable, and Non-shareable using the AWDOMAINS[1:0] and ARDOMAINS[1:0] signals. Inner Shareable is treated identically to Outer Shareable. Transactions to Cacheable Non-shareable memory are not cached in the L3 cache.
- Distributed Virtual Messages (DVM) messages are supported for connecting to an upstream System Memory Management Unit (SMMU).
- Cache stashing is supported, allowing the stash to target either the L3 cache, or a specific L2 cache belonging to a core.
- All ACE5-LiteDVM signals, apart from ARQOS and AWQOS, are included in the ACP interface.

The ACP interface does not support the following features as defined in the AMBA ACE5-LiteDVM protocol specification:

- Barriers are not supported. The BRESPS[1:0] response for any write transaction indicates global observability for the transaction.
- Exclusive accesses are not supported. Therefore, ARLOCK and AWLOCK signals are not present.

> ### Note
>
> For information on how to connect the ACP interface to your system, see
> Functional Integration in the
> Arm® DynamIQ™ Shared Unit-120AE Configuration and Integration Manual.

### Related information

- [ACP features](/documentation/107721/0001/ACP-subordinate-interface/ACP-features?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification and includes support for atomic transactions and cache stashing. Memory tagging is also supported but only to a basic level as defined by the AMBA specification. This allows reading and writing the tags but does not support tag matching on writes.")
- [ACP transactions](/documentation/107721/0001/ACP-subordinate-interface/ACP-transactions?lang=en "The Accelerator Coherency Port (ACP) interface conforms to a subset of the AMBA ACE5-LiteDVM protocol specification. The ACP interface includes support for Cacheable, Non-cacheable, Device, and Atomic memory accesses.")
- [ACP performance](/documentation/107721/0001/ACP-subordinate-interface/ACP-performance?lang=en "For optimum performance, use the following guidelines for Accelerator Coherency Port (ACP) transactions.")
