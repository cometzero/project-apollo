# Changing peripheral port address range

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/Mapping-peripheral-port-address-ranges/Changing-peripheral-port-address-range>

### Changing peripheral port address range

The DynamIQ Shared Unit-120AE (DSU-120AE) supports changing the peripheral port address range to match your system requirements.

### Before you begin

- Ensure both the old and new address ranges are Non-cacheable, for example, this could be done by:

  - Making the memory type a Non-cacheable type or Device type.
  - Making the memory translation invalid.
  - Disabling the L1 and L2 caches in all cores in the DynamIQ Shared Unit-120AE cluster.
- If the old address range is marked as Cacheable, then clean and invalidate all the addresses in that address range. This ensures any cached data is written back on the same interface that it originally came from. This must include a Data Synchronization Barrier (DSB) at the end to ensure the clean and invalidate has completed.

> ### CAUTION
>
> Failure to perform this invalidation could cause system deadlocks if data remains in the L3 cache for the old address range.

### Procedure

1. Reprogram the IMP\_CLUSTERPPSTART\_EL1 and IMP\_CLUSTERPPEND\_EL1 registers as appropriate.
2. Execute a `DSB` and `ISB` instructions to ensure the register updates have completed.
3. You can now map the memory as required or enable the L1 and L2 caches in the cores.

   > ### CAUTION
   >
   > During steps 1 and 2, transactions to the address range being changed might go to either the old port or the new port. Therefore, transactions to this address range might not occur in the expected order.
