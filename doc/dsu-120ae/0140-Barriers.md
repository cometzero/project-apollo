# Barriers

Source: <https://developer.arm.com/documentation/107721/0001/AXI-manager-interface/Barriers>

### Barriers

The DynamIQ Shared Unit-120AE (DSU-120AE) does not support sending barrier transactions to the interconnect. Barriers are always terminated within the cluster.

You must ensure that your interconnect and any peripherals that are connected to it, do not return a write response for a transaction until that transaction is considered complete by a later barrier. This means that the write must be observable to all other managers in the system. Arm expects most peripherals to meet this requirement.
