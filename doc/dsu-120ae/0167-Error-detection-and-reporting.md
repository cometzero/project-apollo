# Error detection and reporting

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Error-detection-and-reporting>

### Error detection and reporting

When the DynamIQ Shared Unit-120AE (DSU-120AE) consumes an error, it raises an Error Recovery Interrupt (ERI).

### Error detection and reporting registers

The following registers are provided:

- The cluster Error Record Feature Register, CLUSTERRAS\_ERR0FR. This is a read-only register that specifies various error record settings.
- The cluster Error Record Control Register, CLUSTERRAS\_ERR0CTLR.
- The cluster Error Record Miscellaneous Register 0-3, CLUSTERRAS\_ERR0MISC0-3. These registers record details of the error location and counts.
- The cluster Pseudo-fault Generation Feature register, CLUSTERRAS\_ERR0PFGF. Read-only register.
- The cluster Error Record Primary Status Register, CLUSTERRAS\_ERR0STATUS.

The cluster Reliability, Availability, and Serviceability (RAS) registers are accessible either from memory-mapped accesses on the utility bus or from System register accesses from the cores.

### Error types

The following describes the different types of errors that can occur in the DSU-120AE and their effects:

- Corrected errors.
- Uncorrectable errors in the L3 data RAMs when read by a core can cause a precise or imprecise Data Abort or Prefetch Abort, depending on the implementation of the core.
- Uncorrectable errors in the L3 data RAMs in a line when this line is being evicted from a cache cause the data to be poisoned. The eviction might be because of a natural eviction, a linefill from a higher level of cache, a cache maintenance operation, or a snoop. If the poisoned line is evicted from the cluster for any reason and the interconnect does not support data poisoning, then the nCLUSTERERRIRQ signal is asserted.
- Uncorrectable errors in the L3 tag RAMs or Snoop Control Unit (SCU) filter RAMs cause the nCLUSTERERRIRQ signal to be asserted.

> ### Note
>
> Arm recommends that the
> ERRIRQ signals are connected to the interrupt controller, so that an interrupt or system error is generated when the signals are asserted.

The fault and error interrupt pins can be cleared by writing to the CLUSTERRAS\_ERR0STATUS register.

When a dirty cache line with an error on the data RAMs is evicted from the cluster, the write on the requester interface still takes place. However, if the error is uncorrectable then:

- If the DSU-120AE is configured with an AXI manager-port, the uncorrected data is written and the error is reported in the RAS registers.
- If the DSU-120AE is configured with a CHI requester-port, the uncorrected data is written but the data poison field indicates that there is a data error.

When a snoop hits on a line with an uncorrectable data error, the following happens:

- If the snoop requires the data, then the data is returned.
- If the DSU-120AE is configured with a CHI requester-port, the snoop response indicates that either the data is poisoned (if supported), or that there is an error.

If a snoop hits on a tag that has an uncorrectable error, then it is treated as a snoop miss. Because the error means that it is not known whether the cache line is valid.

If an Accelerator Coherency Port (ACP) access reads a cache line with an uncorrectable error, then it returns an ACP response to indicate a subordinate error.

Sometimes an error can be counted multiple times. For example, multiple accesses might read the location with the error before the line is evicted.
