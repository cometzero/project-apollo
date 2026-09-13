# PMU features

Source: <https://developer.arm.com/documentation/107721/0001/Performance-Monitors-Extension-support-/PMU-features>

### PMU features

The Performance Monitoring Unit (PMU) includes the following interfaces and counters:

Event interface
:   Events from all other units from across the design are provided to the PMU.

System registers
:   You can program the PMU registers using the System registers. Alternatively, you can access the PMU registers through the memory-mapped Debug APB interface.
    > ### Note
    >
    > The cluster PMU is not accessible when the cluster is in Warm reset, such as during the OFF\_EMU power mode.

Counters
:   The PMU has 64-bit counters that increment when they are enabled, based on events.

PMU register interfaces
:   The DynamIQ Shared Unit-120AE (
    DSU-120AE) supports access to the performance monitor registers from the internal System register interface. The
    DSU-120AE also supports access to the PMU through the memory-mapped Debug APB interface.
