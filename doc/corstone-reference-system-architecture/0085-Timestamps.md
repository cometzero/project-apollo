# Timestamps

Source: <https://developer.arm.com/documentation/102803/latest/Functional-Description/Debug-Infrastructure/Full-Debug-Configuration/Timestamps>

### Timestamps

CRSAS Ma1 provides a debug timestamp input, TSVALUE<B/G>[63:0], that is used by all debug logic that requires timestamp within the subsystem. These are primarily the processor cores in the system.

Since each processor core can be running on different clock rates, the timestamp input updates might occur at a rate that is slower than some of these clocks. CRSAS Ma1 does not specify the including of timestamp interpolators to be deployed in the system for faster cores and as a result, when processor clock to the timestamp update rate ratio increases, especially beyond 10:1, it degrades the timestamp granularity, reducing the ability for you to deduce traced events timings accurately between the two clock domains.
