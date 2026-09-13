# Error reporting and performance monitoring

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Error-detection-and-reporting/Error-reporting-and-performance-monitoring>

### Error reporting and performance monitoring

All detected memory errors and Error Correcting Code (ECC) errors trigger the MEMORY\_ERROR event.

The MEMORY\_ERROR event is counted by the Performance Monitoring Unit (PMU) counters if it is selected and the counter is enabled.

In Secure state, the event is counted only if IMP\_CLUSTERPMMDCR\_EL3.SPME is asserted.

### Related reference

- [PMU events](/documentation/107721/0001/Performance-Monitors-Extension-support-/PMU-events?lang=en "The following table shows the events that are generated and the numbers that the Performance Monitoring Unit (PMU) uses to reference the events.")
