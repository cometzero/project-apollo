# Error signaling by the FMU

Source: <https://developer.arm.com/documentation/107612/0001/Functional-safety-features-of-MHU-320AE/Fault-management-unit/Error-signaling-by-the-FMU>

### Error signaling by the FMU

When a protection mechanism detects an error, it forwards the error to the FMU. If the FMU is enabled, it signals the error to the entire system using the error interrupt signals.

The FMU uses the following error interrupt signals:

- Error recovery interrupt, fmu\_eri signal (ERI)
- Critical error interrupt, fmu\_cri signal (CRI)

The ERI and CRI interrupts are disabled out of reset. Software can use FMU\_ERR<n>CTLR to enable or disable the error reporting through ERI or CRI.

Non-critical errors are reported using ERI and critical errors are reported using CRI. The FMU\_ERR<n>CTLR.CI and FMU\_ERR<n>CTLR.UI bits control this reporting.

Critical errors and non-critical errors can be redirected to different error recovery handlers.
