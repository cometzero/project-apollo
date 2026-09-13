# Supported memory and transaction types

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/Supported-memory-and-transaction-types>

### Supported memory and transaction types

The peripheral port supports all transactions that a core can generate including, atomic transactions, cacheable and non-cacheable accesses, and load and store exclusives.

The peripheral port supports the following transactions:

- Normal Read-Allocate and Write-Allocate cacheable accesses
- Normal Non-cacheable accesses
- Accesses to Device memory types (Device-GRE, nGRE, nGnRE, nGnRnE)
- Atomic transactions
- Load and store exclusive instructions

> ### Note
>
> - Cacheable memory transactions are only coherent outside the DynamIQ Shared Unit-120AE (DSU-120AE) if the peripheral port is configured to use a CHI and the signal BROADCASTOUTERMP is tied HIGH.
> - For Atomic transactions, the signal BROADCASTATOMICMP must be used to indicate if the interconnect supports atomic transactions for the peripheral port.
