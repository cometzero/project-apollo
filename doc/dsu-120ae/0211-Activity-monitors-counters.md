# Activity monitors counters

Source: <https://developer.arm.com/documentation/107721/0001/Activity-Monitors-Extension-support/Activity-monitors-counters>

### Activity monitors counters

The DynamIQ™ Shared Unit-120AE implements five activity monitors counters, 0-4.

Each counter has the following characteristics:

- All events are counted in 64-bit wrapping counters that wrap when they overflow. There is no support for overflow status indication or interrupts.
- Any change in clock frequency, including when a `WFI` and `WFE` instruction stops the clock, can affect any counter.
- All events, 0-4, are fixed. For the list of the cluster activity monitor events, see [Activity monitors events](/documentation/107721/0001/Activity-Monitors-Extension-support/Activity-monitors-events?lang=en "Activity monitors events in the DynamIQ Shared Unit-120AE are all fixed, and they map to the activity monitors counters.").
- The activity monitor counters are reset to zero on a Warm or Cold reset of the power domain of the cluster. When the cluster is not in reset, activity monitoring is available.
