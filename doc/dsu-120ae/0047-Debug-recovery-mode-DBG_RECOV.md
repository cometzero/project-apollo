# Debug recovery mode (DBG_RECOV)

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes/Debug-recovery-mode--DBG-RECOV->

### Debug recovery mode (DBG\_RECOV)

The Debug recovery mode can be used to assist debug of external reset events, such as a watchdog timeout. It allows the contents of the L3 cache RAMs, and the Reliability, Availability, and Serviceability (RAS) registers that were present before a Warm reset to be observable after the reset, as state information is preserved.

In Debug recovery mode, all DynamIQ™ cluster shared logic including the L3 cache RAMs is powered up.

The DSU-120AE invalidates the L3 cache and snoop filter when there is a transition from an Off to an On mode. In Debug recovery mode, cache invalidation is disabled. This allows the contents of the L3 cache that were present before the reset to be observable after the reset. The contents of the L3 cache and snoop filter are preserved and are not altered on the transition back to the On mode.

Debug recovery mode can be entered from any other mode. The cluster Power Policy Unit (PPU) controls entry into this mode.

To preserve the RAS state and cache contents, a transition to the Debug recovery mode can be made from any of the current states. When in Debug recovery mode, the cluster and core PPUs apply a cluster-wide Warm reset. The RAS and cache state are preserved when the core transitions to the On mode.

> ### Note
>
> - Debug recovery mode is strictly for debug purposes. It must not be used for functional purposes, because correct operation of the cluster is not guaranteed when entering this mode.
> - Debug recovery mode can occur at any time with no guarantee of the state of the cluster. A request of this type is accepted immediately, therefore its effects on the core, cluster, or the wider system are UNPREDICTABLE, and a wider system reset might be required. For example, if there were outstanding memory system transactions at the time of the reset, then unless the system interconnect is also reset, these transactions might complete after the reset when the cluster is not expecting them and cause a system deadlock.
> - If the system sends a snoop to the cluster during this mode, then depending on the cluster state:
>
>   - The snoop might get a response and disturb the contents of the caches.
>   - The snoop might not get a response and cause a system deadlock.
> - In the following cases, it might not be possible to enter DBG\_RECOV without a Cold reset of the cluster:
>
>   - When the cluster is in middle of a power transition which cannot complete because of the system hanging.
>   - When the cluster is in the middle of a clock gating transition on the SCLK Q-Channel and the following occur:
>
>     - The Q-Channel does not guarantee the clock availability.
>     - The transition cannot complete because of the system hanging or trying to debug.
>   - The cluster is in Warm reset.
> - You must choose the correct operating mode corresponding to the L3 cache portions and L3 cache slices that were in use before Debug recovery mode.
> - When the PPU\_PTCR.DBG\_RECOV\_PORST\_EN register bit is `0`, the Debug recovery mode performs a warm reset on both the primary and redundant logic. Some of the Dual-Core Lock-Step (DCLS) comparators are on cold reset, so they do not perform warm reset. Because the cluster state can change during the reset, it can rarely lead to a case, when the comparators report a fake fault during Debug recovery.

After the cores and cluster have entered ON mode from DBG\_RECOV, the logic has been reset but the RAM contents are preserved. However, because there could have been outstanding transactions that were partially complete at the time the reset was applied, the contents of the RAMs might be inconsistent. For example, the data RAMs might have been updated by the transaction but the tag RAMs have not. Another example is the snoop filter has been updated but the core caches have not. These inconsistencies can sometimes cause deadlocks or UNPREDICTABLE behavior if normal code is executed. Therefore, Arm recommends analyzing or saving the cache contents without executing normal software. For example, putting the cores into Debug state and executing cache debug operations from Debug state.

After the debug has completed, the whole cluster, and potentially other system components such as the system interconnect, must be reset before normal operation can resume. This should be a cluster Cold reset including the PPUs, using the nRESET signal, to ensure that no inconsistent state remains in the cluster.
