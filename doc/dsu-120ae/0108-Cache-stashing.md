# Cache stashing

Source: <https://developer.arm.com/documentation/107721/0001/L3-cache/Cache-stashing>

### Cache stashing

Cache stashing allows an external agent to request that a line is brought (or stashed) into a cache in the cluster.

Cache stashing can either be performed over the Accelerator Coherency Port (ACP) interface or the CHI requester interface. Stash requests can target either the L3 cache or any of the L2 caches of cores within the cluster. However, the available stashing bandwidth is likely to be higher when stashing to the L3 cache.

> ### Note
>
> - If cores share a complex, then a stash request targeting the L2 cache is allocated into the shared L2 cache of this complex.

On the CHI interface, stash requests (snoops) into both the L2 and L3 caches are supported. The field, StashLPIDValid, indicates the target of the stash, as follows:

- If the field is clear, then the stash is directed to the L3 cache.
- If this field is set, then the stash is directed to an L2 cache of the core the StashLPID field specifies.

On the ACP interface, accesses are implicit stash requests into the L3 cache, by default. Signal AWSTASHLPIDENS indicates that a stash is targeting a L2 cache of a core within the cluster. In this case, signal AWSTASHLPIDS[4:0] indicates which core is being targeted.

The cluster always attempts to allocate a stash request, unless it is heavily utilized and does not have any free buffers. In this case, the cluster drops a stash request to avoid a potential system deadlock.

The Performance Monitoring Unit (PMU) events, in particular those events from 0x0500 to 0x0524, indicates to software how successful the stashing has been. This includes information on how many stash requests were received and how many of the received requests were dropped. For information on PMU events, see [PMU events](/documentation/107721/0001/Performance-Monitors-Extension-support-/PMU-events?lang=en "The following table shows the events that are generated and the numbers that the Performance Monitoring Unit (PMU) uses to reference the events.").

### Related information

- [L3 cache](/documentation/107721/0001/L3-cache?lang=en "All the cores and complexes in the DSU-120AE DynamIQ cluster share the L3 cache.")
- [PMU events](/documentation/107721/0001/Performance-Monitors-Extension-support-/PMU-events?lang=en "The following table shows the events that are generated and the numbers that the Performance Monitoring Unit (PMU) uses to reference the events.")
