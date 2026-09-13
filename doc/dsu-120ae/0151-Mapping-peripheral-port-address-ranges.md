# Mapping peripheral port address ranges

Source: <https://developer.arm.com/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/Mapping-peripheral-port-address-ranges>

### Mapping peripheral port address ranges

The peripheral port supports up to four address ranges for access which you can configure using input bus signals at reset. The first address range can also be configured by programming the System registers IMP\_CLUSTERPPSTART\_EL1 and IMP\_CLUSTERPPEND\_EL1.

You can define the start address and end address of the first address range using the following bus signals:

ASTART0MP[PA-1:20]
:   This bus defines the start address for the first address range, which is inclusive. PA is the largest physical address size of any connected
    core.

AEND0MP[PA-1:20]
:   This bus defines the end address for the first address range, which is exclusive. PA is the largest physical address size of any connected
    core.

Therefore, the address range is defined as ASTART0MP[PA-1:20] <= peripheral port address range < AEND0MP[PA-1:20].

The first address range is configurable to granularity of 1MB. The values for the ASTART0MP[PA-1:20] and AEND0MP[PA-1:20] signals are only captured at reset. The first address range is also captured into registers IMP\_CLUSTERPPSTART\_EL1 and IMP\_CLUSTERPPEND\_EL1 and can be changed at runtime using software.

You can define the start address and end address of the remaining address ranges using the following bus signals:

ASTART<n>MP[PA-1:30]
:   This bus defines the start address for the corresponding address range n, where n = 1, 2, or 3 and PA is the largest physical address size of any connected
    core. The start address is inclusive.

AEND<n>MP[PA-1:30]
:   This bus defines the end address for the corresponding address range n, where n = 1, 2, or 3, and PA is the largest physical address size of any connected
    core. The end address is exclusive.

Therefore, the address range is defined as:

```
ASTART<n>MP[PA-1:20] <= peripheral port address range < AEND<n>MP[PA-1:20]
```

> ### Note
>
> - If an address range is not used, you must set the start address to the end address. For example, tie ASTART1MP and AEND1MP LOW.
> - If DEFAULTP signal is LOW, and both ASTART0MP and AEND0MP are tied LOW then traffic is sent to the main requester port instead of the peripheral port.

These remaining address ranges have a granularity of 1GB. The values for the ASTART<n>MP[PA-1:30] and AEND<n>MP[PA-1:30] signals are only captured at reset. These address ranges are not captured into any registers unlike the first address range.

> ### Note
>
> If you are making address range changes, and there are outstanding transactions to either new or the old address ranges, then it is not guaranteed if the transactions go to the peripheral port or the main
> requester port. See
> [Changing peripheral port address range](/documentation/107721/0001/AXI-or-CHI-requester-peripheral-port/Mapping-peripheral-port-address-ranges/Changing-peripheral-port-address-range?lang=en "The DynamIQ Shared Unit-120AE (DSU-120AE) supports changing the peripheral port address range to match your system requirements.") for more details.

By default, all incoming transaction addresses go to the main requester port or ports, unless both of the following occur in which case they are routed to the peripheral port:

- The transaction is either a core transaction or Accelerator Coherency Port (ACP) transaction.
- The core or ACP transaction matches one of the peripheral port address ranges.

If Distributed Virtual Memory (DVM) operations are supported, these go to the requester port assigned to address target group 0. See [CHI transaction routing with multiple requester ports](/documentation/107721/0001/CHI-requester-interface/CHI-transaction-routing-with-multiple-requester-ports?lang=en "Transactions from the cores are routed, using the address target groups, to one of the CHI bus requester ports based on the transaction type, memory type, and transaction address.") for more details.

However, if the signal DEFAULTP is asserted at reset, then this mapping is inverted and therefore:

- All incoming transaction addresses go to the peripheral port except those that match configured address ranges which are sent to the main requester ports.
- DVM operations are sent to the peripheral port if supported.
  > ### Note
  >
  > To avoid system deadlocks, the peripheral port and main
  > requester ports must be able to complete their accesses independently of each other. However, when a 64-bit AXI peripheral port is configured, it is permissible for a peripheral port access to depend on an Accelerator Coherency Port (ACP) access completing.
