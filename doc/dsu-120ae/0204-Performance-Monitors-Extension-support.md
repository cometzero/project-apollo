# Performance Monitors Extension support

Source: <https://developer.arm.com/documentation/107721/0001/Performance-Monitors-Extension-support->

### Performance Monitors Extension support

The DynamIQ Shared Unit-120AE (DSU-120AE) includes performance monitors that enable you to gather various statistics on the operation of the memory of the cluster during runtime. The performance monitors provide useful information about the behavior of the cluster that you can use when debugging or profiling code.

The Performance Monitoring Unit (PMU) provides six counters. Each counter can count any of the events available in the cluster. The absolute counts that are recorded might vary because of pipeline effects. This has negligible effect except in cases where the counters are enabled for a very short time.
