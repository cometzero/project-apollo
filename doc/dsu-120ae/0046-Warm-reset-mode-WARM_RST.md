# Warm reset mode (WARM_RST)

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes/Warm-reset-mode--WARM-RST->

### Warm reset mode (WARM\_RST)

Warm reset mode applies a Warm reset to the DynamIQ™ cluster shared logic in the cluster.

> ### Note
>
> - If any core is put into Warm reset mode, then the cluster must also be put into Warm reset mode, and the other cores must go into Warm reset mode, or OFF mode.
> - To apply a Warm reset to an individual core, you must program the corresponding Power Policy Unit (PPU) for the core.
> - Warm reset mode is only expected to be used for resets triggered by a system-level issue, such as a watchdog timeout.
> - Warm reset mode can occur at any time with no guarantee of the state of the cluster. A request to transition to Warm reset mode is accepted immediately. Therefore, its effects on the core, complex, cluster, or the wider system are UNPREDICTABLE and a wider reset might be required. For example, if there were outstanding memory transactions at the same time as the reset, then unless the system interconnect is also reset then these transactions might complete after the reset when the cluster is not expecting them and cause a system deadlock.
> - Warm reset mode performs a warm reset on both the primary and redundant logic. Some of the Dual-Core Lock-Step (DCLS) comparators are on cold reset, so they do not perform warm reset. Because the cluster state can change during the reset, it can rarely lead to a case, when the comparators report a fake fault during Warm reset.
