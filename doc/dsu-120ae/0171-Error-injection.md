# Error injection

Source: <https://developer.arm.com/documentation/107721/0001/RAS-extension-support/Error-injection>

### Error injection

Error injection is used to test out the error detection reporting and recording structure by deliberately inserting errors into the error reporting logic.

The injected errors are pseudo-errors only. They cause a report of an error to be signaled but the error injection does not corrupt the target location. Therefore, an injected pseudo-error does not cause any automatic error correction logic to be activated.

Error injection uses the error injection and reporting registers to insert errors. The DynamIQ Shared Unit-120AE (DSU-120AE) can inject any of the following error types:

- Corrected Error (CE)
- Deferred Error (DE)
- Uncontainable Errors (UC)
  - UC error that is a Critical (CI) error

An error can be injected immediately or when a 32-bit counter reaches zero. You can control the value of the counter through the ERRPFGCDN\_EL1 register. The value of the counter decrements on a per clock cycle basis.

Pseudo-errors are injected using the CLUSTERRAS-ERR0PFGCTL, Pseudo-fault Generation Control Register.

Pseudo-errors are triggered by either reads to the snoop filter RAM instances or Long-Term Data Buffer (LTDB) RAMs depending on the type of error that is programmed.

### Errors triggered by reads to the snoop filter RAMs

A UC pseudo-error which is a CI error can be triggered on a look-up in the snoop filter RAM instances. Arm expects that the execution of typical software will trigger the pseudo fault. The pseudo fault can be deliberately triggered by executing a sequence of consecutive load or store transactions to a shareable, cacheable address range where the addresses are not currently cached in the core caches.

### Errors triggered by reads to the LTDB RAMs

All three error types (DE, CE, and UC) which are non-critical errors, can be triggered when there is a read of the LTDB RAM instances. Reads of the LTDB RAMs are most likely to be triggered by either:

- Normal, Non-cacheable, store transactions from the core to the cluster.
- Dirty cache-line evictions from the core to the cluster.

Arm expects that the execution of typical software will trigger the pseudo fault. The pseudo fault can be deliberately triggered by executing a sequence of consecutive Normal Non-cacheable stores to a Normal Non-cacheable address range.

> ### Note
>
> The error injection mechanism only injects pseudo fault reports into the error reporting registers for the purposes of testing error handling and error identification software in real systems. It does not inject actual errors into the hardware.
